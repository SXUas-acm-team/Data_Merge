import json
import os
import shutil
import sys
from pathlib import Path

def process_contest_data(json_file_path, logos_base_path=".", output_base_path="cdp"):
    """
    解析JSON文件，为每个team创建文件夹并复制对应的校徽图片
    
    Args:
        json_file_path: JSON文件路径
        logos_base_path: 校徽图片所在的基础目录
        output_base_path: 输出目录的基础路径
    """
    
    # 读取并解析JSON文件
    organizations = []
    teams = []
    
    print("正在解析JSON文件...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                data_type = data.get('type')
                
                if data_type == 'organizations':
                    org_id = data.get('id')
                    org_data = data.get('data', {})
                    org_name = org_data.get('name', '')
                    # 将Unicode转义序列转换为实际字符
                    if '\\u' in org_name:
                        org_name = org_name.encode('utf-8').decode('unicode_escape')
                    organizations.append({
                            'id': org_id,
                            'name': org_name  # 添加名称到字典中
                    })
            except json.JSONDecodeError as e:
                print(f"警告: 第 {line_num} 行解析JSON时出错: {e}")
                continue
    
    print(f"解析完成: 找到 {len(organizations)} 个学校")
    
    # 显示找到的组织信息
    print("\n找到的组织:")
    for org in organizations:
        print(f"  {org['id']}: {org['name']}")
        
    # 创建输出目录
    output_dir = Path("organizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n开始处理队伍logo...")
    
    # 为每个team处理logo
    success_count = 0
    error_count = 0
    missing_logos = []
    
    for org in organizations:
        org_id = org['id']
        org_name = org['name']
        source_logo_dir = Path(logos_base_path) / org_name
        source_logo_path = source_logo_dir / "logo.png"

        team_output_dir = output_dir / org_id
        team_output_dir.mkdir(parents = True, exist_ok = True)
        destination_logo_path = team_output_dir / "logo.png"

        # 复制logo文件
        if source_logo_path.exists():
            try:
                shutil.copy2(source_logo_path, destination_logo_path)
                print(f"✓ 为学校 {org_id} 复制logo: {org_name}")
                success_count += 1
            except Exception as e:
                print(f"✗ 复制logo失败 (学校 {org}): {e}")
                error_count += 1
                missing_logos.append(f"{org_name} (学校 {org})")
        else:
            print(f"✗ 未找到logo文件: {source_logo_path}")
            error_count += 1
            missing_logos.append(f"{org_name} (学校 {org_id})")

    # 输出处理结果
    print(f"\n" + "="*50)
    print(f"处理完成!")
    print(f"成功: {success_count}")
    print(f"失败: {error_count}")
    print(f"输出目录: {output_dir}")
    
    if missing_logos:
        print(f"\n缺少logo的组织:")
        for missing in missing_logos:
            print(f"  - {missing}")

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python script.py <json_file_path> [logos_dir] [output_dir]")
        print("示例:")
        print("  python script.py ./test.ndjson")
        print("  python script.py ./contest.json ./logos ./output")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    # 可选参数
    logos_base_path = sys.argv[2] if len(sys.argv) > 2 else "."
    output_base_path = sys.argv[3] if len(sys.argv) > 3 else "."  # 或者直接去掉这个参数
    
    # 验证JSON文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误: JSON文件 '{json_file_path}' 不存在")
        sys.exit(1)
    
    # 开始处理
    process_contest_data(json_file_path, logos_base_path, output_base_path)
    
    print("\n程序执行完毕!")

if __name__ == "__main__":
    main()