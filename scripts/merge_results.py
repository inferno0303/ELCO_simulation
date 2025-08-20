import csv
from pathlib import Path


def merge_csv_files(output_file_name: str = "merge_results.csv"):
    results_dir = Path(__file__).resolve().parent.parent / 'results'
    out_file = results_dir / output_file_name

    csv_files = sorted(results_dir.glob("*.csv"))
    if not csv_files:
        print("⚠️ 没有找到任何 CSV 文件")
        return

    with open(out_file, "w", newline='', encoding="utf-8") as outfile:
        writer = None
        for i, file in enumerate(csv_files):
            with open(file, "r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                header = next(reader)  # 读取表头
                if i == 0:  # 只写一次表头
                    writer = csv.writer(outfile)
                    writer.writerow(header)
                # 写入数据行
                for row in reader:
                    writer.writerow(row)

    print(f"✅ 已合并 {len(csv_files)} 个 CSV 文件，输出到: {out_file}")


if __name__ == "__main__":
    merge_csv_files()
