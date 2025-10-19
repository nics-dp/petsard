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

        Raises:
            ConfigError: 如果配置中缺少 'source' 欄位，或 source 格式不正確
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

        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    def create(self, data: dict) -> dict[str, Any]:
        """
        處理資料並提取 schema 資訊

        Args:
            data (dict): 資料字典，由 ReporterOperator.set_input() 生成
                格式參考 BaseReporter._verify_create_input()

        Returns:
            dict[str, Any]: 處理後的 schema 資料字典
                key: 完整實驗名稱
                value: Schema 物件
        """
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
                # 從 DataFrame 推斷 schema
                schema_dict = self._infer_schema_from_dataframe(df)
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

            # 生成包含所有 source 模組名稱的檔名（類似 save_data 的做法）
            source_names = "-".join(self.config["source"])
            csv_filename = f"{self.config['output']}_schema_{source_names}_summary.csv"
            df_output.to_csv(csv_filename, index=False, encoding="utf-8")
            self._logger.info(f"已保存 schema summary 到 {csv_filename}")

        return saved_schemas

    def _infer_schema_from_dataframe(self, df) -> dict[str, Any]:
        """
        從 DataFrame 推斷 schema 結構

        Args:
            df: pandas DataFrame

        Returns:
            dict: schema 字典，包含欄位資訊
        """
        schema = {"columns": {}, "shape": {"rows": len(df), "columns": len(df.columns)}}

        # 為每個欄位記錄資訊
        for col in df.columns:
            col_info = {
                "dtype": str(df[col].dtype),
                "nullable": bool(df[col].isna().any()),
                "unique_count": int(df[col].nunique()),
            }

            # 如果是數值型別，添加統計資訊
            if df[col].dtype.kind in "biufc":  # bool, int, unsigned int, float, complex
                if not df[col].isna().all():
                    min_val = df[col].min()
                    max_val = df[col].max()
                    mean_val = df[col].mean()

                    # 根據資料型別決定統計值的精度
                    if df[col].dtype.kind in "biu":  # bool, int, unsigned int
                        # 整數型別：四捨五入為整數
                        col_info["statistics"] = {
                            "min": int(round(min_val)),
                            "max": int(round(max_val)),
                            "mean": int(round(mean_val)),
                        }
                    else:  # float, complex
                        # 浮點數型別：偵測資料精度並限制小數位數
                        decimal_places = self._detect_decimal_places(df[col])
                        col_info["statistics"] = {
                            "min": round(float(min_val), decimal_places),
                            "max": round(float(max_val), decimal_places),
                            "mean": round(float(mean_val), decimal_places),
                        }
                else:
                    col_info["statistics"] = {
                        "min": None,
                        "max": None,
                        "mean": None,
                    }

            # 如果是物件類型（通常是字串），記錄樣本值
            elif df[col].dtype == "object" or df[col].dtype.name == "category":
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
        例如: source, age_dtype, age_nullable, age_min, age_max, income_dtype, ...

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
                        row[f"{column_name}_{stat_key}"] = stat_value
                elif key == "categories" and isinstance(value, list):
                    # 類別值列表，轉為字串
                    row[f"{column_name}_categories"] = "|".join(str(v) for v in value)
                elif not isinstance(value, (dict, list)):
                    # 其他簡單類型 (dtype, nullable, unique_count 等)
                    row[f"{column_name}_{key}"] = value

        return row
