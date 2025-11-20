#!/usr/bin/env python3
"""
Coverage Report Generator
Generate clear and understandable test coverage reports
"""

import logging
import os
import sys
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


def parse_coverage_xml(xml_file):
    """Parse coverage.xml file"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Get overall coverage
        line_rate = float(root.attrib.get("line-rate", 0))
        overall_coverage = line_rate * 100

        # Get coverage for each package
        packages = []
        for package in root.findall(".//package"):
            package_name = package.attrib.get("name", "Unknown")
            package_line_rate = float(package.attrib.get("line-rate", 0))
            package_coverage = package_line_rate * 100

            # Get class coverage
            classes = []
            for cls in package.findall(".//class"):
                class_name = cls.attrib.get("name", "Unknown")
                class_filename = cls.attrib.get("filename", "Unknown")
                class_line_rate = float(cls.attrib.get("line-rate", 0))
                class_coverage = class_line_rate * 100

                classes.append(
                    {
                        "name": class_name,
                        "filename": class_filename,
                        "coverage": class_coverage,
                    }
                )

            packages.append(
                {"name": package_name, "coverage": package_coverage, "classes": classes}
            )

        return {"overall_coverage": overall_coverage, "packages": packages}
    except ET.ParseError as e:
        logger.error(f"Failed to parse coverage.xml: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing coverage.xml: {e}", exc_info=True)
        return None


def get_coverage_grade(coverage):
    """Return grade based on coverage percentage"""
    if coverage >= 90:
        return "🎉 Excellent", "green"
    elif coverage >= 80:
        return "✅ Good", "yellow"
    elif coverage >= 70:
        return "⚠️ Fair", "orange"
    else:
        return "❌ Needs Improvement", "red"


def generate_markdown_report(coverage_data):
    """Generate Markdown format coverage report"""
    if not coverage_data:
        return "❌ Unable to generate coverage report"

    overall_coverage = coverage_data["overall_coverage"]
    grade, color = get_coverage_grade(overall_coverage)

    report = []
    report.append("## 📊 Test Coverage Report")
    report.append("")
    report.append("### 🎯 Overall Coverage")
    report.append(f"**{overall_coverage:.1f}%** - {grade}")
    report.append("")

    # Coverage explanation
    report.append("### 📖 Coverage Explanation")
    report.append("- **90%+**: 🎉 Excellent - Very comprehensive test coverage")
    report.append("- **80-89%**: ✅ Good - Good test coverage, consider adding boundary tests")
    report.append("- **70-79%**: ⚠️ Fair - Recommend adding more test cases")
    report.append("- **<70%**: ❌ Needs Improvement - Strongly recommend increasing test coverage")
    report.append("")

    # Module coverage details
    if coverage_data["packages"]:
        report.append("### 📁 Module Coverage Details")
        report.append("")

        for package in coverage_data["packages"]:
            package_grade, _ = get_coverage_grade(package["coverage"])
            report.append(f"#### 📦 {package['name']}")
            report.append(f"**Coverage**: {package['coverage']:.1f}% - {package_grade}")
            report.append("")

            if package["classes"]:
                report.append("| File | Coverage | Status |")
                report.append("|------|----------|--------|")

                for cls in package["classes"]:
                    filename = os.path.basename(cls["filename"])
                    cls_grade, _ = get_coverage_grade(cls["coverage"])
                    report.append(
                        f"| `{filename}` | {cls['coverage']:.1f}% | {cls_grade} |"
                    )

                report.append("")

    # Improvement suggestions
    if overall_coverage < 80:
        report.append("### 💡 Improvement Suggestions")
        report.append("")
        if overall_coverage < 70:
            report.append("- 🚨 **Urgent**: Coverage too low, prioritize adding basic functionality tests")
            report.append("- 📝 Recommend writing at least one test case for each public method")
            report.append(
                "- 🔍 Use `pytest --cov-report=html` to generate detailed report and view uncovered code"
            )
        else:
            report.append("- 📈 Recommend adding tests for boundary conditions and exceptional cases")
            report.append("- 🧪 Consider adding integration tests to cover more use cases")
            report.append("- 🎯 Focus on improving test coverage for core modules")
        report.append("")

    return "\n".join(report)


def main():
    """Main function"""
    if len(sys.argv) != 2:
        logger.error("Usage: python coverage_report.py <coverage.xml>")
        sys.exit(1)

    xml_file = sys.argv[1]
    if not os.path.exists(xml_file):
        logger.error(f"Coverage file not found: {xml_file}")
        sys.exit(1)

    coverage_data = parse_coverage_xml(xml_file)
    report = generate_markdown_report(coverage_data)
    print(report)


if __name__ == "__main__":
    main()
