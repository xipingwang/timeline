import re
from datetime import datetime
from textwrap import wrap

def generate_timeline_svg(events, output_file="timeline.svg", dark_mode=False):
    """
    根据事件数据生成SVG时间轴图表
    :param events: 事件列表，每个事件为字典格式：
                  {"date": "YYYY-MM-DD", "time": "HH:MM", "text": "事件描述"}
    :param output_file: 输出SVG文件名
    :param dark_mode: 是否使用深色模式
    """
    # 预处理事件数据
    processed_events = []
    for event in events:
        try:
            date_obj = datetime.strptime(event["date"], "%Y-%m-%d")
            processed_events.append({
                "date_obj": date_obj,
                "date_str": event["date"],
                "time": event["time"],
                "text": event["text"],
            })
        except ValueError:
            print(f"忽略无效日期格式的事件: {event}")

    # 按日期排序
    processed_events.sort(key=lambda x: x["date_obj"])

    # 分组同一天的事件
    grouped_events = {}
    for event in processed_events:
        date_str = event["date_str"]
        if date_str not in grouped_events:
            grouped_events[date_str] = []
        grouped_events[date_str].append(event)

    # 计算布局参数
    date_count = len(grouped_events)
    svg_width = max(1100, date_count * 180)  # 日期宽度150 + 间距10
    svg_height = 500
    timeline_y = 100
    date_spacing = 160  # 固定间距
    current_x = 80  # 初始位置

    # 颜色主题
    if dark_mode:
        bg_color = "#222222"
        text_color = "#eeeeee"
        secondary_text = "#aaaaaa"
        line_color = "#555555"
        connector_color = "#666666"
    else:
        bg_color = "#ffffff"
        text_color = "#333333"
        secondary_text = "#555555"
        line_color = "#333333"
        connector_color = "#999999"

    # SVG头部
    svg_content = f'''<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" 
                      xmlns="http://www.w3.org/2000/svg" font-family="Arial">
    <!-- 样式定义 -->
    <style>
        .background {{ fill: {bg_color}; }}
        .timeline-line {{ stroke: {line_color}; stroke-width: 2; }}
        .day-connector {{ stroke: {connector_color}; stroke-dasharray: 3,2; stroke-width: 1; }}
        .event-circle {{ fill: #4a6da7; stroke: {bg_color}; stroke-width: 1; r: 5; }}
        .event-circle.main-anchor {{ fill: #e74c3c; r: 6; }}
        .date-label {{ font-size: 11px; fill: {text_color}; text-anchor: middle; }}
        .time-label {{ font-size: 10px; fill: {secondary_text}; text-anchor: start; }}
        .event-label {{ font-size: 10px; fill: {text_color}; text-anchor: start; }}
        .day-group {{ stroke: none; fill: none; }}
    </style>

    <!-- 背景 -->
    <rect width="100%" height="100%" class="background" />

    <!-- 主时间轴线 -->
    <line x1="50" y1="{timeline_y}" x2="{svg_width-50}" y2="{timeline_y}" class="timeline-line" />\n'''

    # 生成每个日期的事件组
    max_height = timeline_y
    for date_str, day_events in grouped_events.items():
        # 计算该日期需要的垂直空间
        event_heights = []
        for event in day_events:
            # 支持手动换行符\n和自动换行
            lines = []
            for paragraph in event["text"].split('\n'):
                lines.extend(wrap(paragraph, width=14))  # 每行约20个字符
            event_heights.append(len(lines) * 15 + 10)  # 每行15px
        
        total_height = sum(event_heights) + len(day_events) * 10  # 事件间距10px
        
        # 主锚点
        svg_content += f'    <!-- {date_str} -->\n'
        svg_content += f'    <g transform="translate({current_x},{timeline_y})">\n'
        svg_content += f'        <circle cx="0" cy="0" r="6" class="event-circle main-anchor"/>\n'
        svg_content += f'        <text x="0" y="-20" class="date-label">{date_str}</text>\n'
        
        # 事件组容器
        svg_content += f'        <g class="day-group" transform="translate(0,25)">\n'
        svg_content += f'            <line x1="0" y1="-15" x2="0" y2="{total_height}" class="day-connector"/>\n'
        
        # 每个事件
        y_offset = 0
        for i, event in enumerate(day_events):
            # 处理换行文本
            lines = []
            for paragraph in event["text"].split('\n'):
                lines.extend(wrap(paragraph, width=14))
            
            svg_content += f'            <g transform="translate(0,{y_offset})">\n'
            svg_content += f'                <circle cx="0" cy="0" r="5" class="event-circle"/>\n'
            svg_content += f'                <text x="15" y="5" class="time-label">{event["time"]}</text>\n'
            
            # 输出每行文本
            for j, line in enumerate(lines):
                svg_content += f'                <text x="15" y="{20 + j*15}" class="event-label">{line}</text>\n'
            
            svg_content += '            </g>\n'
            y_offset += len(lines) * 15 + 20  # 移动到下一个事件位置
        
        # 关闭组
        svg_content += '        </g>\n'
        svg_content += '    </g>\n\n'
        
        # 更新最大高度
        max_height = max(max_height, timeline_y + total_height + 50)
        current_x += date_spacing  # 固定间距移动

    # 更新SVG高度
    svg_content = svg_content.replace(
        f'height="{svg_height}"', 
        f'height="{max_height}"'
    ).replace(
        f'viewBox="0 0 {svg_width} {svg_height}"',
        f'viewBox="0 0 {svg_width} {max_height}"'
    )

    # SVG尾部
    svg_content += '</svg>'

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"时间轴图表已生成: {output_file}")

# 测试数据（包含换行符的示例）
test_events = [
    {"date": "2023-01-15", "time": "09:00", "text": "项目Alpha正式启动会议，讨论初期规划和资源分配"},
    {"date": "2023-03-10", "time": "11:15", "text": "第一版原型设计评审会议，收集各部门反馈意见"},
    {"date": "2023-05-10", "time": "08:30", "text": "晨会：确定项目里程碑和关键交付节点，讨论季度目标。\n目标是在2023年实现100万用户注册，实现100万订单交易。\n预计完成时间：2023年6月30日。相关人员：产品经理、市场团队、技术团队。"},
    {"date": "2023-05-10", "time": "14:15", "text": "收到客户重要需求变更通知，影响后端API设计和数据库架构，需要紧急修改。\n问题描述：当前API设计存在性能瓶颈，需要优化查询逻辑，以提高响应速度。\n预计解决时间：1天内。相关人员：后端开发团队。"},
    {"date": "2023-05-10", "time": "19:00", "text": "紧急修复版本部署，解决生产环境关键安全漏洞，系统稳定性更新"},
    {"date": "2023-07-29", "time": "08:00", "text": "首次公开演示（线上直播），超过500名观众参与，获得积极反馈"},
    {"date": "2023-07-29", "time": "09:00", "text": "第二次公开演示（线上直播）"},
    {"date": "2023-11-11", "time": "00:00", "text": "双十一促销活动正式开始，推出限时折扣方案和会员专属优惠"},
    {"date": "2023-11-11", "time": "09:45", "text": "服务器达到流量峰值1.2万QPS，系统稳定运行，无重大故障"},
    {"date": "2023-11-11", "time": "23:59", "text": "当日销售额统计完成，\n创下公司单日销售新纪录，同比增长120%"},
    {"date": "2024-03-08", "time": "07:30", "text": "国际妇女节专题活动上线，展示女性员工成就和职业发展故事"},
    {"date": "2024-03-08", "time": "12:00", "text": "用户反馈收集截止，共收到328条有价值的建议，将纳入下季度改进"},
    {"date": "2024-03-08", "time": "18:20", "text": "社交媒体宣传视频发布，\n24小时内获得10万次观看和2000次分享"}
]

if __name__ == "__main__":
    # 使用测试数据生成示例（浅色模式）
    generate_timeline_svg(test_events, "timeline_light.svg", dark_mode=False)
    
    # 生成深色模式示例
    generate_timeline_svg(test_events, "timeline_dark.svg", dark_mode=True)
    
    print("已生成浅色(timeline_light.svg)和深色(timeline_dark.svg)两个版本")
