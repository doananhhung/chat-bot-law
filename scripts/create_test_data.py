from fpdf import FPDF
import os

def create_dummy_pdf(filename="test_law.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    text = """
    CONG HOA XA HOI CHU NGHIA VIET NAM
    Doc lap - Tu do - Hanh phuc
    
    LUAT THU NGHIEM
    
    Dieu 1. Pham vi dieu chinh
    Luat nay quy dinh ve viec thu nghiem he thong Chatbot AI.
    
    Dieu 2. Doi tuong ap dung
    1. Cac lap trinh vien tham gia du an.
    2. Cac nguoi dung thu nghiem he thong.
    
    Dieu 3. Nguyen tac
    Dam bao tinh chinh xac, khach quan va trung thuc.
    """
    
    # FPDF with standard font doesn't support full utf-8 nicely without loading font, 
    # so I used unsigned text for safety in this dummy generator.
    
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line.strip(), ln=1, align='L')
        
    output_path = os.path.join("data", "raw", filename)
    pdf.output(output_path)
    print(f"Created {output_path}")

if __name__ == "__main__":
    create_dummy_pdf()

