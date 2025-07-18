import pandas as pd

# === 步骤 1：读取用户的 TF 列表 ===
input_excel = "prmt3.xlsx"  
tf_column = "TF" 

tf_df = pd.read_excel(input_excel)
# 保留原始TF列（原大小写），并创建新列供匹配使用
tf_df["TF_upper"] = tf_df[tf_column].astype(str).str.upper()

# === 步骤 2：读取 TRRUST 数据（人类）并统一大写 ===
trrust_df = pd.read_csv("trrust_rawdata.human.tsv", sep="\t", header=None)
trrust_df.columns = ["TF", "Target", "Mode", "PMID"]
trrust_df["TF_upper"] = trrust_df["TF"].astype(str).str.upper()

# === 步骤 3：建立 TF → 调控模式的映射 ===
tf_mode_map = {}

for tf in tf_df["TF_upper"]:
    matches = trrust_df[trrust_df["TF_upper"] == tf]
    if not matches.empty:
        modes = matches["Mode"].str.lower().unique()
        if "activation" in modes and "repression" in modes:
            tf_mode_map[tf] = "activation & repression"
        elif "activation" in modes:
            tf_mode_map[tf] = "activation"
        elif "repression" in modes:
            tf_mode_map[tf] = "repression"
        else:
            tf_mode_map[tf] = "unknown"
    else:
        tf_mode_map[tf] = "缺乏证据"

# === 步骤 4：写入结果 ===
tf_df["调控模式"] = tf_df["TF_upper"].map(tf_mode_map)
tf_df.drop(columns=["TF_upper"], inplace=True)  # 可选：删除中间列

output_file = "annotated_tf_list.xlsx"
tf_df.to_excel(output_file, index=False)

print(f"已完成，处理后的结果保存在：{output_file}")
