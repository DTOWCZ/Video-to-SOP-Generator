"""
PDF Generator Module
Creates professional SOP PDF documents with images and structured content
"""

import os
import base64
import tempfile
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, 
    PageBreak, Table, TableStyle, KeepTogether
)


class SOPPDFGenerator:
    """Generate professional SOP PDF documents"""
    
    def __init__(self, page_size=letter):
        """
        Initialize PDF Generator
        
        Args:
            page_size: Page size (letter or A4)
        """
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Step number style
        self.styles.add(ParagraphStyle(
            name='StepNumber',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#d63031'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # Safety warning style
        self.styles.add(ParagraphStyle(
            name='SafetyWarning',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#d63031'),
            backColor=colors.HexColor('#fff5f5'),
            borderColor=colors.HexColor('#d63031'),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=10
        ))
    
    def generate_sop_pdf(
        self, 
        sop_data: Dict, 
        frames: List[Dict],
        output_path: str,
        company_name: str = "Your Company"
    ):
        """
        Generate SOP PDF from structured data
        
        Args:
            sop_data: Dictionary containing SOP structure
            frames: List of extracted frames (with 'image_data' and 'timestamp')
            output_path: Output PDF file path
            company_name: Company name for header
        """
        print(f"Generating PDF: {output_path}")
        
        # List to track temporary files for cleanup
        self.temp_files = []
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Build content
            story = []
            
            # Add title page
            story.extend(self._create_title_page(sop_data, company_name))
            story.append(PageBreak())
            
            # Add table of contents
            story.extend(self._create_table_of_contents(sop_data))
            story.append(PageBreak())
            
            # Add safety notes if present
            if "safety_notes" in sop_data and sop_data["safety_notes"]:
                story.extend(self._create_safety_section(sop_data["safety_notes"]))
                story.append(PageBreak())
            
            # Add procedure steps
            story.extend(self._create_steps_section(sop_data, frames))
            
            # Build PDF
            doc.build(story)
            print(f"PDF generated successfully: {output_path}")
            
        finally:
            # Clean up temporary image files
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Warning: Could not delete temp file {temp_file}: {e}")
    
    def _create_title_page(self, sop_data: Dict, company_name: str) -> List:
        """Create title page elements"""
        elements = []
        
        # Company name
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(company_name, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Document type
        elements.append(Paragraph(
            "STANDARD OPERATING PROCEDURE",
            self.styles['Heading2']
        ))
        elements.append(Spacer(1, 0.5*inch))
        
        # Title
        elements.append(Paragraph(
            sop_data.get("title", "Untitled Procedure"),
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Description
        if "description" in sop_data:
            elements.append(Paragraph(
                sop_data["description"],
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Document info table
        doc_info = [
            ["Document Date:", datetime.now().strftime("%B %d, %Y")],
            ["Revision:", "1.0"],
            ["Total Steps:", str(len(sop_data.get("steps", [])))]
        ]
        
        table = Table(doc_info, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_table_of_contents(self, sop_data: Dict) -> List:
        """Create table of contents"""
        elements = []
        
        elements.append(Paragraph("TABLE OF CONTENTS", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # TOC entries
        toc_data = []
        
        if "safety_notes" in sop_data and sop_data["safety_notes"]:
            toc_data.append(["Safety Information", "3"])
        
        for step in sop_data.get("steps", []):
            step_title = f"Step {step['step_number']}: {step['instruction'][:50]}..."
            toc_data.append([step_title, str(4 + step['step_number'])])
        
        if toc_data:
            toc_table = Table(toc_data, colWidths=[5*inch, 1*inch])
            toc_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(toc_table)
        
        return elements
    
    def _create_safety_section(self, safety_notes: List[str]) -> List:
        """Create safety information section"""
        elements = []
        
        elements.append(Paragraph(
            "⚠️ SAFETY INFORMATION",
            self.styles['SectionHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        for note in safety_notes:
            elements.append(Paragraph(
                f"• {note}",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_steps_section(self, sop_data: Dict, frames: List[Dict]) -> List:
        """Create procedure steps section with images"""
        elements = []
        
        elements.append(Paragraph("PROCEDURE", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Create a dictionary mapping timestamps to frames for quick lookup
        frame_lookup = {frame['timestamp']: frame['image_data'] for frame in frames}
        
        for step in sop_data.get("steps", []):
            step_elements = []
            
            # Step header
            step_header = f"Step {step['step_number']}"
            step_elements.append(Paragraph(step_header, self.styles['StepNumber']))
            
            # Instruction
            step_elements.append(Paragraph(
                step['instruction'],
                self.styles['CustomBody']
            ))
            
            # Add image at timestamp
            try:
                timestamp = step.get('timestamp_seconds', 0)
                
                # Find the closest frame to the requested timestamp
                closest_timestamp = min(frame_lookup.keys(), key=lambda t: abs(t - timestamp))
                frame_data_base64 = frame_lookup[closest_timestamp]
                
                # Decode base64 image data
                frame_data = base64.b64decode(frame_data_base64)
                
                # Save to temporary file (ReportLab Image needs a file path)
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(frame_data)
                    temp_image_path = temp_file.name
                
                # Track for cleanup after PDF is built
                self.temp_files.append(temp_image_path)
                
                # Create ReportLab Image with file path
                img = Image(temp_image_path, width=4*inch, height=3*inch)
                step_elements.append(Spacer(1, 0.1*inch))
                step_elements.append(img)
                
                # Caption
                caption = f"Image at {timestamp:.1f} seconds"
                step_elements.append(Paragraph(
                    caption,
                    self.styles['Normal']
                ))
                
            except Exception as e:
                print(f"Could not add image for step {step['step_number']}: {e}")
            
            # Reasoning/notes
            if 'reasoning' in step:
                step_elements.append(Spacer(1, 0.1*inch))
                step_elements.append(Paragraph(
                    f"<i>Note: {step['reasoning']}</i>",
                    self.styles['Normal']
                ))
            
            # Keep step together on same page
            elements.append(KeepTogether(step_elements))
            elements.append(Spacer(1, 0.3*inch))
        
        return elements