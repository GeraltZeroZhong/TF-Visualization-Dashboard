import pandas as pd
from Bio.Seq import Seq

def reverse_complement(seq):
    return str(Seq(seq).reverse_complement())

def get_alignment(seq, start, stop, user_start, user_stop):
    start = int(start)
    stop = int(stop)
    user_start = int(user_start)
    user_stop = int(user_stop)

    alignment = []

    for i in range(user_start, user_stop + 1):  # 只关注目标区间
        if start <= i <= stop:
            idx = i - start
            if 0 <= idx < len(seq):
                alignment.append(seq[idx])
            else:
                alignment.append('-')
        else:
            alignment.append('-')

    return ''.join(alignment)


    # 调整到期望长度
    expected_length = abs(user_stop - user_start) + 1
    if len(aln_str) < expected_length:
        aln_str = aln_str.ljust(expected_length, '-')
    elif len(aln_str) > expected_length:
        aln_str = aln_str[:expected_length]

    return aln_str

def process_file(input_excel, output_excel, output_txt, user_start, user_stop):
    df = pd.read_excel(input_excel)

    # 类型转换
    df["Start"] = pd.to_numeric(df["Start"], errors="coerce")
    df["Stop"] = pd.to_numeric(df["Stop"], errors="coerce")
    df["Pvalue"] = pd.to_numeric(df["Pvalue"], errors="coerce")

    # 任务 1：生成 SEQ
    def compute_seq(row):
        seq = row["Mached Sequence"]
        if not isinstance(seq, str) or pd.isna(seq):
            return ""
        seq_fixed = seq if row["Strand"] == "+" else reverse_complement(seq)
        try:
            start = int(row["Start"])
            stop = int(row["Stop"])
            expected_len = stop - start + 1
            if len(seq_fixed) < expected_len:
                seq_fixed = seq_fixed + '-' * (expected_len - len(seq_fixed))
            elif len(seq_fixed) > expected_len:
                seq_fixed = seq_fixed[:expected_len]
        except:
            pass
        return seq_fixed

    df["SEQ"] = df.apply(compute_seq, axis=1)

    # 任务 2：生成 alignment
    
    def compute_alignment(row):
        
        try:
            start, stop, pval = row["Start"], row["Stop"], row["Pvalue"]
            if pd.notna(start) and pd.notna(stop) and pd.notna(pval):
                if pval < 0.001 and not (stop < user_start or start > user_stop):
                    return get_alignment(row["SEQ"], start, stop, user_start, user_stop)
            return None
        except Exception as e:
            print(f"[ERROR] 处理行失败: TF={row.get('TF')}, Source={row.get('Source')}, Start={row.get('Start')}, Stop={row.get('Stop')}")
            raise e

    df["alignment"] = df.apply(compute_alignment, axis=1)

    # 保存 Excel
    df.to_excel(output_excel, index=False)
    print(f"[INFO] 已保存处理后的 Excel 文件到：{output_excel}")

    # 任务 3：输出 TXT，alignment 去重，保证长度一致
    expected_length = abs(user_stop - user_start) + 1
    unique_alignments = dict()

    for _, row in df.iterrows():
        aln = row["alignment"]
        if isinstance(aln, str) and len(aln) == expected_length:
            if aln not in unique_alignments:
                header = f">{row['TF']}{row['Source']}"
                unique_alignments[aln] = header
        elif isinstance(aln, str):
            print(f"[WARNING] alignment 长度不符（{len(aln)} != {expected_length}），跳过: TF={row['TF']}, Source={row['Source']}")

    with open(output_txt, "w") as f:
        for aln, header in unique_alignments.items():
            f.write(f"{header}\n{aln}\n")

    print(f"[INFO] alignment 去重后共写入 {len(unique_alignments)} 条，保存至：{output_txt}")






# 主程序入口
if __name__ == "__main__":
    input_excel = "annotated_tf_list.xlsx"
    output_excel = "processed_output.xlsx"
    output_txt = "alignment_output.txt"

    # 用户输入区间
    user_start = int(input("请输入区间起始位置："))
    user_stop = int(input("请输入区间结束位置："))

    process_file(input_excel, output_excel, output_txt, user_start, user_stop)
