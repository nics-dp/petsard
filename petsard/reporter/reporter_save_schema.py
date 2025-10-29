"""
ReporterSaveSchema - 輸出指定 source 模組所使用的 schema yaml 檔
"""

import logging
from typing import Any

import yaml

from petsard.exceptions import ConfigError
from petsard.reporter.reporter_base import BaseReporter, RegexPatterns


class ReporterSaveSchema(BaseReporter):
    """
    Schema 輸出報告器

    此 reporter 會根據 source 參數指定的模組，輸出對應的 schema 資訊到 YAML 檔案。
    可用於追蹤和記錄各個處理階段的資料結構變化。
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): 配置字典。
                - method (str): 報告方法（必須為 'SAVE_SCHEMA'）
                - source (str | List[str]): 資料來源模組名稱
                    支援的模組：'Loader', 'Splitter', 'Preprocessor', 'Synthesizer',
                               'Postprocessor', 'Constrainer'
                - output (str, optional): 輸出檔案名稱前綴，預設為 'petsard'
                - yaml_output (bool, optional): 是否輸出 YAML 檔案，預設為 False
                - properties (str | List[str], optional): 要輸出的屬性名稱，預設為所有屬性
                    支援的屬性：'type', 'category', 'dtype', 'nullable', 'unique_count',
                               'precision', 'min', 'max', 'mean', 'std', 'categories'
                    注意：
                    - 'type': schema 定義的類型（如 'str', 'int', 'float64'）
                    - 'category': schema 中的 category 標記（True/False）
                    - 'dtype': 實際 pandas dtype（如 'float64', 'object'）
                    - 'precision': 數值欄位的小數位數（從 type_attr 中取得）

        Raises:
            ConfigError: 如果配置中缺少 'source' 欄位，或 source/properties 格式不正確
        """
        super().__init__(config)

        # source 應該是字串或字串列表: Union[str, List[str]]
        if "source" not in self.config:
            raise ConfigError("Configuration must include 'source' field")
        elif not isinstance(self.config["source"], str | list) or (
            isinstance(self.config["source"], list)
            and not all(isinstance(item, str) for item in self.config["source"])
        ):
            raise ConfigError("'source' must be a string or list of strings")

        # 將 source 轉換為列表（如果是字串）
        if isinstance(self.config["source"], str):
            self.config["source"] = [self.config["source"]]

        # 處理 properties 參數
        if "properties" in self.config:
            if isinstance(self.config["properties"], str):
                self.config["properties"] = [self.config["properties"]]
            elif not isinstance(self.config["properties"], list) or not all(
                isinstance(item, str) for item in self.config["properties"]
            ):
                raise ConfigError("'properties' must be a string or list of strings")

        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    def create(self, data: dict) -> dict[str, Any]:
        """
        處理資料並提取 schema 資訊

        Args:
            data (dict): 資料字典，由 ReporterOperator.set_input() 生成
                格式參考 BaseReporter._verify_create_input()
                可能包含 'metadata' key，其中包含各模組的 Schema

        Returns:
            dict[str, Any]: 處理後的 schema 資料字典
                key: 完整實驗名稱
                value: Schema 物件
        """
        # 提取並存儲 metadata（如果有）
        if "metadata" in data:
            self._metadata_dict = data.pop("metadata")
            self._logger.debug(
                f"Received metadata for {len(self._metadata_dict)} modules"
            )
        else:
            self._metadata_dict = {}

        # 提取並存儲 schema_history（如果有）
        if "schema_history" in data:
            self._schema_history_dict = data.pop("schema_history")
            self._logger.debug(
                f"Received schema history for {len(self._schema_history_dict)} modules"
            )
            # 記錄每個模組的 snapshot 數量
            for module, history in self._schema_history_dict.items():
                self._logger.debug(f"  - {module}: {len(history)} snapshots")
        else:
            self._schema_history_dict = {}

        # 驗證輸入資料
        self._verify_create_input(data)

        processed_schemas = {}

        # 遍歷所有資料項目
        for full_expt_tuple, df in data.items():
            if df is None:
                continue

            # 檢查最後的模組是否在 source 列表中
            # full_expt_tuple 格式: ('Loader', 'default', 'Preprocessor', 'scaler')
            if len(full_expt_tuple) >= 2:
                last_module = full_expt_tuple[-2]
                last_expt_name = full_expt_tuple[-1]

                # 移除可能的後綴 "_[xxx]" 以匹配 source
                clean_expt_name = RegexPatterns.POSTFIX_REMOVAL.sub("", last_expt_name)

                # 檢查模組名稱或實驗名稱是否在 source 中
                if (
                    last_module in self.config["source"]
                    or clean_expt_name in self.config["source"]
                ):
                    # 生成完整實驗名稱
                    full_expt_name = "_".join(
                        [
                            f"{full_expt_tuple[i]}[{full_expt_tuple[i + 1]}]"
                            for i in range(0, len(full_expt_tuple), 2)
                        ]
                    )
                    processed_schemas[full_expt_name] = df

        # 特殊處理：展開 Preprocessor 的 schema history
        # metadata_dict 中可能包含 "Preprocessor_步驟名稱" 格式的 key
        for source in self.config["source"]:
            if source in ["Preprocessor", "Postprocessor"]:
                # 查找所有以此模組開頭的 metadata entries
                for meta_key in list(self._metadata_dict.keys()):
                    if meta_key.startswith(f"{source}_"):
                        # 提取步驟名稱
                        step_name = meta_key[
                            len(source) + 1 :
                        ]  # 去掉 "Preprocessor_" 前綴

                        # 找到對應的 data entry（如果有的話）
                        # 但對於 schema history，我們主要關注 metadata
                        # 所以即使沒有對應的 data，也要處理

                        # 構建一個合成的 full_expt_name，包含步驟資訊
                        # 從 processed_schemas 中找到原始的 Preprocessor entry
                        base_expt_name = None
                        for expt_name in processed_schemas.keys():
                            if f"{source}[" in expt_name:
                                base_expt_name = expt_name
                                break

                        if base_expt_name:
                            # 在模組名稱後添加步驟資訊
                            # 例如: "Loader[x]_Preprocessor[y]" -> "Loader[x]_Preprocessor[y_step_name]"
                            step_expt_name = (
                                base_expt_name.replace(
                                    f"{source}[", f"{source}[{step_name}_"
                                )
                                .replace(f"[{step_name}_", "[")
                                .replace("]", f"_{step_name}]")
                            )

                            # 使用與 base 相同的 dataframe（或空的）
                            processed_schemas[step_expt_name] = processed_schemas.get(
                                base_expt_name
                            )

                            self._logger.debug(
                                f"Added schema history entry: {step_expt_name}"
                            )

        self._logger.info(f"已處理 {len(processed_schemas)} 個模組的 schema 資訊")
        return processed_schemas

    def report(self, processed_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        生成並保存 schema 報告

        預設輸出 CSV 格式（攤平的表格），每個 source 一行
        可選輸出 YAML 格式（yaml_output=True）

        Args:
            processed_data (dict[str, Any] | None): 處理後的資料
                key: 實驗名稱
                value: pandas DataFrame（用於推斷 schema）

        Returns:
            dict[str, Any]: 已保存的 schema 資料
        """
        if not processed_data:
            self._logger.warning("沒有資料可處理，跳過 schema 報告生成")
            return {}

        saved_schemas = {}
        flattened_rows = []

        for expt_name, df in processed_data.items():
            if df is None:
                self._logger.debug(f"跳過空資料: {expt_name}")
                continue

            try:
                # 嘗試獲取對應的 metadata
                metadata = self._get_metadata_for_expt(expt_name)

                # 從 DataFrame 推斷 schema，並傳入 metadata
                schema_dict = self._infer_schema_from_dataframe(df, metadata)
                saved_schemas[expt_name] = schema_dict

                # 攤平整個 source 的 schema 為單一行
                row = self._flatten_source_schema(expt_name, schema_dict)
                flattened_rows.append(row)

                # 可選：保存為 YAML 檔案
                if self.config.get("yaml_output", False):
                    output_filename = f"{self.config['output']}_schema_{expt_name}.yaml"
                    self._save_schema_to_yaml(schema_dict, output_filename)
                    self._logger.info(f"已保存 YAML schema 到 {output_filename}")

            except Exception as e:
                self._logger.error(f"處理 {expt_name} 時發生錯誤: {e}")
                continue

        # 預設輸出：summary CSV（包含 source 名稱在檔名中）
        if flattened_rows:
            import pandas as pd

            df_output = pd.DataFrame(flattened_rows)

            # 對列進行排序：source 在第一列，其他列按欄位名稱排序
            # 格式：[欄位名稱]_屬性，這樣同一欄位的所有屬性會聚在一起
            columns = list(df_output.columns)

            # 分離 source 和其他列
            if "source" in columns:
                columns.remove("source")
                # 對其他列排序
                sorted_columns = ["source"] + sorted(columns)
            else:
                sorted_columns = sorted(columns)

            # 重新排序 DataFrame
            df_output = df_output[sorted_columns]

            # 生成包含所有 source 模組名稱的檔名（類似 save_data 的做法）
            source_names = "-".join(self.config["source"])
            csv_filename = f"{self.config['output']}_schema_{source_names}_summary.csv"
            df_output.to_csv(csv_filename, index=False, encoding="utf-8")
            self._logger.info(f"已保存 schema summary 到 {csv_filename}")

        return saved_schemas

    def _get_metadata_for_expt(self, expt_name: str):
        """
        獲取實驗名稱對應的 metadata

        支援格式：
        - "Loader[default]_Preprocessor[v1]" (標準格式)
        - "Loader[default]_Preprocessor[v1_after_encoder]" (schema history 格式)

        Args:
            expt_name: 實驗名稱

        Returns:
            Schema 或 None
        """
        self._logger.debug(f"Looking up metadata for: {expt_name}")

        if not hasattr(self, "_metadata_dict"):
            self._logger.warning("No _metadata_dict attribute found")
            return None

        # 記錄所有可用的 metadata keys
        self._logger.debug(
            f"Available metadata keys: {list(self._metadata_dict.keys())}"
        )

        # 找到最後一個模組部分
        # 例如: "Loader[default]_Preprocessor[v1_after_encoder]"
        # 我們需要提取 "Preprocessor" 和可能的 "after_encoder"
        parts = expt_name.split("_")
        self._logger.debug(f"Experiment name parts: {parts}")

        # 找到最後一個包含方括號的部分
        last_module_part = None
        for part in reversed(parts):
            if "[" in part and "]" in part:
                last_module_part = part
                last_module_index = parts.index(part)
                break

        if not last_module_part:
            self._logger.warning(f"No module part with brackets found in: {expt_name}")
            return None

        # 提取模組名稱（方括號之前的部分）
        last_module = last_module_part.split("[")[0]
        self._logger.debug(f"Last module: {last_module}")

        # 檢查是否有步驟後綴
        # 方括號內容格式可能是: "v1_after_encoder"
        bracket_content = last_module_part.split("[")[1].rstrip("]")
        self._logger.debug(f"Bracket content: {bracket_content}")

        # 檢查方括號後是否還有更多下劃線分隔的部分（這些可能是步驟名稱）
        # 例如: "Loader[default]_Preprocessor[v1]_after_encoder"
        remaining_parts = parts[last_module_index + 1 :]
        self._logger.debug(f"Remaining parts after module: {remaining_parts}")

        if remaining_parts:
            # 有步驟後綴，例如: ["after", "encoder"]
            step_suffix = "_".join(remaining_parts)
            meta_key = f"{last_module}_{step_suffix}"
            self._logger.debug(f"Trying step metadata key: {meta_key}")
            metadata = self._metadata_dict.get(meta_key)

            if metadata:
                self._logger.debug(f"Found schema history metadata: {meta_key}")
                return metadata
            else:
                self._logger.debug(f"Step metadata key not found: {meta_key}")

        # 沒有步驟後綴，使用標準查找
        self._logger.debug(f"Trying standard metadata key: {last_module}")
        metadata = self._metadata_dict.get(last_module)
        if metadata:
            self._logger.debug(f"Found standard metadata: {last_module}")
            return metadata
        else:
            self._logger.warning(f"Standard metadata key not found: {last_module}")

        return None

    def _infer_schema_from_dataframe(self, df, metadata=None) -> dict[str, Any]:
        """
        從 DataFrame 推斷 schema 結構

        Args:
            df: pandas DataFrame
            metadata: Schema metadata (optional)

        Returns:
            dict: schema 字典，包含欄位資訊
        """
        schema = {"columns": {}, "shape": {"rows": len(df), "columns": len(df.columns)}}

        # 取得要輸出的屬性列表
        properties = self.config.get("properties", None)

        # Debug: 記錄 metadata 資訊
        if metadata:
            self._logger.debug(
                f"Processing with metadata. Attributes count: {len(metadata.attributes) if hasattr(metadata, 'attributes') else 0}"
            )
        else:
            self._logger.warning("No metadata provided for schema inference")

        # 為每個欄位記錄資訊
        for col in df.columns:
            col_info = {}

            # 從 metadata 獲取屬性
            schema_type = None
            schema_category = None
            schema_nullable = None
            schema_precision = None

            if (
                metadata
                and hasattr(metadata, "attributes")
                and col in metadata.attributes
            ):
                attr = metadata.attributes[col]
                schema_type = attr.type

                # 從 type_attr 讀取屬性
                if attr.type_attr:
                    schema_category = attr.type_attr.get("category", False)
                    schema_nullable = attr.type_attr.get("nullable", True)
                    schema_precision = attr.type_attr.get("precision")
                else:
                    schema_category = False
                    schema_nullable = True

                self._logger.debug(
                    f"Column {col}: type={schema_type}, category={schema_category}, nullable={schema_nullable}, precision={schema_precision}"
                )
            else:
                # 沒有 metadata 時，從資料推斷
                dtype_str = str(df[col].dtype)

                # 推斷 category
                if dtype_str == "category":
                    schema_category = True
                elif df[col].dtype == "object" and len(df[col]) > 0:
                    unique_ratio = len(df[col].unique()) / len(df[col])
                    schema_category = unique_ratio < 0.05
                else:
                    schema_category = False

                # 推斷 nullable
                schema_nullable = (
                    bool(df[col].isna().any()) if len(df[col]) > 0 else True
                )

                self._logger.debug(
                    f"Column {col}: No metadata found, inferred category={schema_category}, nullable={schema_nullable}"
                )

            # 基本屬性 - type 和 dtype 都應該輸出
            if properties is None or "type" in properties:
                # 優先使用 schema type，沒有則使用推斷的類型
                if schema_type:
                    col_info["type"] = schema_type
                else:
                    # 從 dtype 推斷 type（簡化版映射）
                    dtype_str = str(df[col].dtype)
                    type_mapping = {
                        "int8": "int8",
                        "int16": "int16",
                        "int32": "int32",
                        "int64": "int64",
                        "float32": "float32",
                        "float64": "float64",
                        "bool": "boolean",
                        "object": "string",
                        "category": "string",
                    }
                    col_info["type"] = type_mapping.get(dtype_str, dtype_str)

            if properties is None or "category" in properties:
                # 輸出 category（True/False），永遠不應該是 None
                col_info["category"] = schema_category
                self._logger.debug(
                    f"Column {col}: Set category in col_info = {schema_category}"
                )

            if properties is None or "dtype" in properties:
                # dtype 永遠輸出（實際的 pandas dtype）
                col_info["dtype"] = str(df[col].dtype)

            # Precision（使用已經取得的 schema_precision）
            if properties is None or "precision" in properties:
                if schema_precision is not None:
                    col_info["precision"] = schema_precision

            if properties is None or "nullable" in properties:
                # 使用已經取得的 schema_nullable
                col_info["nullable"] = (
                    schema_nullable if schema_nullable is not None else True
                )

            if properties is None or "unique_count" in properties:
                col_info["unique_count"] = int(df[col].nunique())

            # 如果是數值型別，添加統計資訊
            if df[col].dtype.kind in "biufc":  # bool, int, unsigned int, float, complex
                # 檢查是否需要任何統計屬性
                stats_needed = (
                    properties is None
                    or "min" in properties
                    or "max" in properties
                    or "mean" in properties
                    or "std" in properties
                )

                if stats_needed and not df[col].isna().all():
                    statistics = {}

                    # 根據資料型別決定統計值的精度
                    if df[col].dtype.kind in "biu":  # bool, int, unsigned int
                        # 整數型別：四捨五入為整數
                        if properties is None or "min" in properties:
                            statistics["min"] = int(round(df[col].min()))
                        if properties is None or "max" in properties:
                            statistics["max"] = int(round(df[col].max()))
                        if properties is None or "mean" in properties:
                            statistics["mean"] = int(round(df[col].mean()))
                        if properties is None or "std" in properties:
                            statistics["std"] = int(round(df[col].std()))
                    else:  # float, complex
                        # 浮點數型別：偵測資料精度並限制小數位數
                        decimal_places = self._detect_decimal_places(df[col])
                        if properties is None or "min" in properties:
                            statistics["min"] = round(
                                float(df[col].min()), decimal_places
                            )
                        if properties is None or "max" in properties:
                            statistics["max"] = round(
                                float(df[col].max()), decimal_places
                            )
                        if properties is None or "mean" in properties:
                            statistics["mean"] = round(
                                float(df[col].mean()), decimal_places
                            )
                        if properties is None or "std" in properties:
                            statistics["std"] = round(
                                float(df[col].std()), decimal_places
                            )

                    if statistics:
                        col_info["statistics"] = statistics
                elif stats_needed:
                    # 全部為 NA 的情況
                    statistics = {}
                    if properties is None or "min" in properties:
                        statistics["min"] = None
                    if properties is None or "max" in properties:
                        statistics["max"] = None
                    if properties is None or "mean" in properties:
                        statistics["mean"] = None
                    if properties is None or "std" in properties:
                        statistics["std"] = None
                    if statistics:
                        col_info["statistics"] = statistics

            # 如果是物件類型（通常是字串），記錄樣本值
            elif (df[col].dtype == "object" or df[col].dtype.name == "category") and (
                properties is None or "categories" in properties
            ):
                unique_values = df[col].dropna().unique()
                if len(unique_values) <= 10:  # 只有少量唯一值時才記錄
                    col_info["categories"] = [str(v) for v in unique_values]

            schema["columns"][str(col)] = col_info

        return schema

    def _detect_decimal_places(self, series, max_check: int = 100) -> int:
        """
        偵測浮點數欄位的小數位數

        Args:
            series: pandas Series（浮點數型別）
            max_check: 最多檢查的資料筆數（預設100）

        Returns:
            int: 小數位數（最多6位）
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return 2  # 預設2位小數

        decimal_places = 0
        # 只檢查前 max_check 個值以提高效率
        for val in non_null.head(max_check):
            # 轉換為字串並檢查小數位數
            val_str = f"{val:.10f}".rstrip("0").rstrip(".")
            if "." in val_str:
                decimal_places = max(decimal_places, len(val_str.split(".")[1]))

        # 限制最多6位小數
        return min(decimal_places, 6) if decimal_places > 0 else 2

    def _save_schema_to_yaml(self, schema_dict: dict, filename: str) -> None:
        """
        將 schema 字典保存為 YAML 檔案

        Args:
            schema_dict: schema 字典
            filename: 輸出檔案名稱
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump(
                    schema_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            self._logger.debug(f"Schema 已寫入檔案: {filename}")
        except Exception as e:
            self._logger.error(f"寫入 YAML 檔案時發生錯誤: {e}")
            raise

    def _flatten_source_schema(self, source: str, schema_dict: dict) -> dict:
        """
        將整個 source 的 schema 攤平為單一 row

        一個 source 變成一行，所有欄位的所有屬性攤平成列
        使用 [欄位名稱]_屬性 格式，方便按字母排序時同一欄位的屬性會聚集在一起
        例如: source, [age]_dtype, [age]_nullable, [age]_min, [age]_max, [income]_dtype, ...

        Args:
            source: 來源實驗名稱
            schema_dict: 完整的 schema 字典

        Returns:
            dict: 攤平的 row 資料，source 是第一個欄位
        """
        row = {"source": source}

        # 遍歷所有欄位
        for column_name, column_info in schema_dict["columns"].items():
            # 第一層屬性
            for key, value in column_info.items():
                if key == "statistics" and isinstance(value, dict):
                    # 第二層：statistics (如 min, max, mean)
                    for stat_key, stat_value in value.items():
                        row[f"[{column_name}]_{stat_key}"] = stat_value
                elif key == "categories" and isinstance(value, list):
                    # 類別值列表，轉為字串
                    row[f"[{column_name}]_categories"] = "|".join(str(v) for v in value)
                elif not isinstance(value, (dict, list)):
                    # 其他簡單類型 (dtype, nullable, unique_count, category, type 等)
                    row[f"[{column_name}]_{key}"] = value

        return row
