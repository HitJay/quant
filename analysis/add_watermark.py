"""给PDF加水印"""
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
font_path = '/mnt/c/Windows/Fonts/simhei.ttf'
pdfmetrics.registerFont(TTFont('SimHei', font_path))

# 水印参数
watermark_text = "付费专享 · 复旦杰伦"
opacity = 0.15  # 透明度
rotation = 45   # 旋转角度
font_size = 40  # 字体大小

def create_watermark(text, pagesize):
    """创建水印PDF页面"""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=pagesize)
    
    # 设置透明度和颜色
    c.setFillAlpha(opacity)
    c.setFillColorRGB(0.5, 0.5, 0.5)  # 灰色
    c.setFont('SimHei', font_size)
    
    # 计算水印位置 - 铺满整个页面
    page_width, page_height = pagesize
    
    # 旋转画布
    c.saveState()
    
    # 创建网格状水印
    x_spacing = 400  # 水平间距
    y_spacing = 200  # 垂直间距
    
    for y in range(-200, int(page_height) + 200, y_spacing):
        for x in range(-200, int(page_width) + 200, x_spacing):
            c.saveState()
            c.translate(x, y)
            c.rotate(rotation)
            c.drawCentredString(0, 0, text)
            c.restoreState()
    
    c.restoreState()
    c.save()
    
    packet.seek(0)
    return PdfReader(packet)

def add_watermark_to_pdf(input_path, output_path, watermark_text):
    """给PDF每一页添加水印"""
    # 读取原始PDF
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # 获取第一页的尺寸
    first_page = reader.pages[0]
    page_width = first_page.mediabox.width
    page_height = first_page.mediabox.height
    pagesize = (page_width, page_height)
    
    # 创建水印
    watermark_pdf = create_watermark(watermark_text, pagesize)
    watermark_page = watermark_pdf.pages[0]
    
    # 给每一页添加水印
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        
        # 合并水印层
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    # 写入新文件
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"水印已添加: {output_path}")

# 使用
input_pdf = 'output/commodity-rotation/paid_report.pdf'
output_pdf = 'output/commodity-rotation/paid_report_watermarked.pdf'

add_watermark_to_pdf(input_pdf, output_pdf, watermark_text)
