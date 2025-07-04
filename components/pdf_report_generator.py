"""
Professional PDF Report Generator for Project Structure Analysis
Generates comprehensive reports with project structure, WBE analysis, and cost distribution
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import json
import tempfile
import os
import logging
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import our new reliable chart generator
from .chart_generators import create_chart_generator

# Keep Plotly imports as fallback but don't use them by default
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
        PageBreak, Image, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus.tableofcontents import TableOfContents
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ProjectStructurePDFGenerator:
    """Professional PDF report generator for project structure analysis"""
    
    def __init__(self, data: Dict[str, Any], file_type: str = None):
        self.data = data
        self.file_type = file_type or self._detect_file_type()
        self.styles = None
        self.story = []
        self.charts_temp_files = []
        
        # Setup logging
        self.logger = logging.getLogger('PDFGenerator')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        
        # Initialize the new chart generator
        self.chart_generator = create_chart_generator()
        
    def _detect_file_type(self) -> str:
        """Detect file type from data structure"""
        if 'wbe_analysis' in self.data or any('wbe' in str(cat).lower() for group in self.data.get('product_groups', []) for cat in group.get('categories', [])):
            return 'analisi_profittabilita'
        return 'pre'
    
    def _setup_styles(self):
        """Setup PDF styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E4057')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2E4057'),
            keepWithNext=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#3A5F7D'),
            keepWithNext=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.HexColor('#F8F9FA')
        ))
    
    def _safe_float(self, value, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _create_chart_image_reliable(self, data: List[Dict], chart_type: str, 
                                   x_key: str, y_key: str, title: str, filename: str) -> Optional[str]:
        """Create chart image using reliable chart generator"""
        
        # Skip chart generation if environment variable is set
        if os.environ.get('SKIP_PDF_CHARTS', 'false').lower() == 'true':
            self.logger.info(f"Skipping chart {filename} due to SKIP_PDF_CHARTS=true")
            return None
        
        try:
            self.logger.debug(f"Creating reliable chart: {filename}")
            
            if chart_type == 'pie':
                chart_path = self.chart_generator.create_pie_chart(data, y_key, x_key, title, filename)
            elif chart_type == 'bar':
                chart_path = self.chart_generator.create_bar_chart(data, x_key, y_key, title, filename)
            else:
                self.logger.warning(f"Unknown chart type: {chart_type}")
                return None
            
            if chart_path and os.path.exists(chart_path):
                # Add to our cleanup list
                self.charts_temp_files.append(chart_path)
                self.logger.debug(f"Reliable chart created: {filename}")
                return chart_path
            else:
                self.logger.warning(f"Chart creation failed for {filename}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error creating reliable chart {filename}: {str(e)}")
            return None
    
    def _cleanup_temp_files(self):
        """Clean up temporary chart files"""
        # Clean up our own temp files
        for temp_file in self.charts_temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                self.logger.warning(f"Could not clean up temp file {temp_file}: {e}")
        self.charts_temp_files = []
        
        # Clean up chart generator temp files
        try:
            self.chart_generator.cleanup_temp_files()
        except Exception as e:
            self.logger.warning(f"Could not clean up chart generator files: {e}")
    
    def _add_table_of_contents(self):
        """Add table of contents"""
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(fontSize=14, name='TOCHeading1', leftIndent=20, fontName='Helvetica-Bold'),
            ParagraphStyle(fontSize=12, name='TOCHeading2', leftIndent=40, fontName='Helvetica'),
        ]
        
        self.story.append(Paragraph("Table of Contents", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 20))
        
        # Manual TOC for simplicity
        toc_items = [
            "1. Executive Summary",
            "2. Project Overview", 
            "3. Financial Summary",
            "4. Group Analysis",
            "5. Category Analysis & WBE Distribution",
            "6. Profitability Analysis",
            "7. Cost Distribution Analysis",
            "8. Detailed Breakdown",
            "9. Recommendations"
        ]
        
        for item in toc_items:
            self.story.append(Paragraph(item, self.styles['CustomNormal']))
        
        self.story.append(PageBreak())
    
    def _add_executive_summary(self):
        """Add executive summary section"""
        self.story.append(Paragraph("1. Executive Summary", self.styles['CustomHeading1']))
        
        project_info = self.data.get('project', {})
        totals = self.data.get('totals', {})
        
        # Project basics
        project_id = project_info.get('id', 'N/A')
        customer = project_info.get('customer', 'N/A')
        
        # Financial totals
        total_listino = self._safe_float(totals.get('total_pricelist', 0))
        total_cost = self._safe_float(totals.get('total_cost', 0))
        total_offer = self._safe_float(totals.get('total_offer', 0))
        
        # Calculate margins
        listino_margin = total_listino - total_cost
        listino_margin_perc = (listino_margin / total_listino * 100) if total_listino > 0 else 0
        
        if total_offer > 0:
            offer_margin = total_offer - total_cost
            offer_margin_perc = (offer_margin / total_offer * 100) if total_offer > 0 else 0
        else:
            offer_margin = listino_margin
            offer_margin_perc = listino_margin_perc
        
        # Count items and groups
        product_groups = self.data.get('product_groups', [])
        total_groups = len(product_groups)
        total_categories = sum(len(group.get('categories', [])) for group in product_groups)
        total_items = sum(len(cat.get('items', [])) for group in product_groups for cat in group.get('categories', []))
        
        summary_text = f"""
        <b>Project ID:</b> {project_id}<br/>
        <b>Customer:</b> {customer}<br/>
        <b>File Type:</b> {self.file_type.replace('_', ' ').title()}<br/><br/>
        
        <b>Structure Overview:</b><br/>
        • {total_groups:,} Product Groups<br/>
        • {total_categories:,} Categories<br/>
        • {total_items:,} Items<br/><br/>
        
        <b>Financial Overview:</b><br/>
        • Total Listino: €{total_listino:,.2f}<br/>
        • Total Cost: €{total_cost:,.2f}<br/>
        • Listino Margin: €{listino_margin:,.2f} ({listino_margin_perc:.1f}%)<br/>
        """
        
        if total_offer > 0:
            summary_text += f"• Total Offer: €{total_offer:,.2f}<br/>• Offer Margin: €{offer_margin:,.2f} ({offer_margin_perc:.1f}%)<br/>"
        
        # Add WBE analysis if available
        if self.file_type == 'analisi_profittabilita':
            wbe_count = self._count_wbes()
            if wbe_count > 0:
                summary_text += f"<br/><b>WBE Analysis:</b><br/>• {wbe_count} Work Breakdown Elements identified<br/>"
        
        self.story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        self.story.append(Spacer(1, 20))
        
        # Add summary metrics table
        summary_data = [
            ['Metric', 'Value', 'Percentage'],
            ['Total Listino', f'€{total_listino:,.2f}', '100.0%'],
            ['Total Cost', f'€{total_cost:,.2f}', f'{(total_cost/total_listino*100):,.1f}%' if total_listino > 0 else '0.0%'],
            ['Listino Margin', f'€{listino_margin:,.2f}', f'{listino_margin_perc:.1f}%']
        ]
        
        if total_offer > 0:
            summary_data.append(['Total Offer', f'€{total_offer:,.2f}', f'{(total_offer/total_listino*100):,.1f}%' if total_listino > 0 else '0.0%'])
            summary_data.append(['Offer Margin', f'€{offer_margin:,.2f}', f'{offer_margin_perc:.1f}%'])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(summary_table)
        self.story.append(PageBreak())
    
    def _count_wbes(self) -> int:
        """Count unique WBEs in the data"""
        wbes = set()
        for group in self.data.get('product_groups', []):
            for category in group.get('categories', []):
                wbe = category.get('wbe', '').strip()
                if wbe:
                    wbes.add(wbe)
        return len(wbes)
    
    def _add_project_overview(self):
        """Add project overview section"""
        self.story.append(Paragraph("2. Project Overview", self.styles['CustomHeading1']))
        
        project_info = self.data.get('project', {})
        
        # Project information table
        project_data = [
            ['Field', 'Value'],
            ['Project ID', project_info.get('id', 'N/A')],
            ['Customer', project_info.get('customer', 'N/A')],
            ['Project Name', project_info.get('name', 'N/A')],
            ['Listino', project_info.get('listino', 'N/A')],
        ]
        
        # Add sales information if available
        sales_info = project_info.get('sales_info', {})
        if sales_info:
            project_data.extend([
                ['Area Manager', sales_info.get('area_manager', 'N/A')],
                ['Author', sales_info.get('author', 'N/A')],
                ['Agent', sales_info.get('agent', 'N/A')],
            ])
        
        # Add dates if available
        if 'created_date' in project_info:
            project_data.append(['Created Date', project_info.get('created_date', 'N/A')])
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(project_table)
        self.story.append(PageBreak())
    
    def _add_group_analysis(self):
        """Add group analysis section"""
        try:
            self.logger.info("Starting group analysis section")
            self.story.append(Paragraph("4. Group Analysis", self.styles['CustomHeading1']))
            
            # Add timeout for entire section
            import time
            start_time = time.time()
            max_duration = 120  # 2 minutes max for group analysis
            
            product_groups = self.data.get('product_groups', [])
            self.logger.info(f"Found {len(product_groups)} product groups")
            
            if not product_groups:
                self.logger.warning("No product groups found in data")
                self.story.append(Paragraph("No product groups found in the data.", self.styles['CustomNormal']))
                return
            
            # Prepare group data
            self.logger.info("Processing group data...")
            group_data = []
            
            for i, group in enumerate(product_groups):
                try:
                    # Check timeout
                    if time.time() - start_time > max_duration:
                        self.logger.error("Group analysis timeout exceeded, stopping processing")
                        self.story.append(Paragraph("Analysis timeout - partial results shown", self.styles['CustomNormal']))
                        break
                    
                    self.logger.debug(f"Processing group {i+1}/{len(product_groups)}")
                    
                    group_id = group.get('group_id', 'Unknown')
                    group_name = group.get('group_name', 'Unnamed')
                    categories = group.get('categories', [])
                    
                    self.logger.debug(f"Group {group_id}: {len(categories)} categories")
                    
                    # Calculate totals safely
                    group_total = 0
                    group_cost = 0
                    total_items = 0
                    
                    for cat in categories:
                        try:
                            if self.file_type == 'analisi_profittabilita':
                                cat_total = self._safe_float(cat.get('pricelist_subtotal', 0))
                                cat_cost = self._safe_float(cat.get('cost_subtotal', 0))
                            else:
                                items = cat.get('items', [])
                                cat_total = sum(self._safe_float(item.get('pricelist_total_price', 0)) for item in items)
                                cat_cost = sum(self._safe_float(item.get('total_cost', 0)) for item in items)
                            
                            group_total += cat_total
                            group_cost += cat_cost
                            total_items += len(cat.get('items', []))
                            
                        except Exception as e:
                            self.logger.error(f"Error processing category in group {group_id}: {str(e)}")
                            continue
                    
                    # Calculate margin safely
                    margin = group_total - group_cost
                    margin_perc = (margin / group_total * 100) if group_total > 0 else 0
                    
                    group_data.append({
                        'Group ID': str(group_id),
                        'Group Name': str(group_name)[:30] + '...' if len(str(group_name)) > 30 else str(group_name),
                        'Categories': len(categories),
                        'Items': total_items,
                        'Total (€)': group_total,
                        'Cost (€)': group_cost,
                        'Margin (€)': margin,
                        'Margin (%)': margin_perc
                    })
                    
                    self.logger.debug(f"Group {group_id} processed successfully: €{group_total:,.0f}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing group {i}: {str(e)}")
                    # Add a placeholder entry for failed groups
                    group_data.append({
                        'Group ID': f'Error-{i}',
                        'Group Name': 'Processing Error',
                        'Categories': 0,
                        'Items': 0,
                        'Total (€)': 0,
                        'Cost (€)': 0,
                        'Margin (€)': 0,
                        'Margin (%)': 0
                    })
                    continue
            
            self.logger.info(f"Successfully processed {len(group_data)} groups")
            
            # Create group analysis table
            self.logger.info("Creating group analysis table...")
            table_data = [['Group ID', 'Group Name', 'Categories', 'Items', 'Total (€)', 'Cost (€)', 'Margin (€)', 'Margin (%)']]
            
            for group in group_data:
                try:
                    table_data.append([
                        str(group['Group ID']),
                        str(group['Group Name']),
                        f"{group['Categories']:,}",
                        f"{group['Items']:,}",
                        f"€{group['Total (€)']:,.0f}",
                        f"€{group['Cost (€)']:,.0f}",
                        f"€{group['Margin (€)']:,.0f}",
                        f"{group['Margin (%)']:.1f}%"
                    ])
                except Exception as e:
                    self.logger.error(f"Error formatting group data: {str(e)}")
                    # Add a safe fallback row
                    table_data.append(['Error', 'Error', '0', '0', '€0', '€0', '€0', '0.0%'])
            
            try:
                self.logger.info("Creating table object...")
                groups_table = Table(table_data, colWidths=[1*inch, 1.5*inch, 0.7*inch, 0.7*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
                groups_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                self.story.append(groups_table)
                self.story.append(Spacer(1, 20))
                self.logger.info("Group table added successfully")
                
            except Exception as e:
                self.logger.error(f"Error creating group table: {str(e)}")
                self.story.append(Paragraph(f"Error creating group table: {str(e)}", self.styles['CustomNormal']))
            
            # Add group distribution chart using reliable method
            try:
                self.logger.info("Creating group distribution chart...")
                
                if group_data and len(group_data) > 0:
                    # Filter out zero-value groups for chart
                    chart_data = [g for g in group_data if g['Total (€)'] > 0]
                    self.logger.debug(f"Chart data filtered: {len(chart_data)} groups with value > 0")
                    
                    if chart_data and len(chart_data) <= 15:  # Reasonable limit for readability
                        self.logger.debug("Creating reliable pie chart...")
                        chart_path = self._create_chart_image_reliable(
                            chart_data, 'pie', 'Group ID', 'Total (€)', 
                            'Total Value Distribution by Group', 'group_distribution.png'
                        )
                        
                        if chart_path and os.path.exists(chart_path):
                            self.story.append(Image(chart_path, width=6*inch, height=3*inch))
                            self.logger.info("Group chart added successfully")
                        else:
                            self.logger.info("Chart creation skipped or failed - continuing without chart")
                            
                    elif len(chart_data) > 15:
                        self.logger.info(f"Too many groups for chart ({len(chart_data)}), skipping for readability")
                    else:
                        self.logger.info("No positive-value data for group chart")
                else:
                    self.logger.info("No group data available for chart")
                    
            except Exception as e:
                self.logger.warning(f"Group chart creation failed: {str(e)} - continuing without chart")
                # Don't fail the whole process for chart errors
            
            self.story.append(PageBreak())
            self.logger.info("Group analysis section completed successfully")
            
        except Exception as e:
            self.logger.error(f"Critical error in group analysis: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Add error message to PDF
            self.story.append(Paragraph(f"Error generating group analysis: {str(e)}", self.styles['CustomNormal']))
            self.story.append(PageBreak())
    
    def _add_category_wbe_analysis(self):
        """Add category analysis focused on WBE"""
        self.story.append(Paragraph("5. Category Analysis & WBE Distribution", self.styles['CustomHeading1']))
        
        # Collect WBE data
        wbe_data = {}
        category_data = []
        
        for group in self.data.get('product_groups', []):
            for category in group.get('categories', []):
                cat_id = category.get('category_id', 'Unknown')
                cat_name = category.get('category_name', 'Unnamed')
                wbe = category.get('wbe', '').strip()
                
                # Calculate category totals
                if self.file_type == 'analisi_profittabilita':
                    cat_total = self._safe_float(category.get('pricelist_subtotal', 0))
                    cat_cost = self._safe_float(category.get('cost_subtotal', 0))
                else:
                    items = category.get('items', [])
                    cat_total = sum(self._safe_float(item.get('pricelist_total_price', 0)) for item in items)
                    cat_cost = sum(self._safe_float(item.get('total_cost', 0)) for item in items)
                
                category_data.append({
                    'Group': group.get('group_id', 'Unknown'),
                    'Category': cat_id,
                    'Name': cat_name[:25] + '...' if len(cat_name) > 25 else cat_name,
                    'WBE': wbe or 'Unassigned',
                    'Items': len(category.get('items', [])),
                    'Total (€)': cat_total,
                    'Cost (€)': cat_cost,
                    'Margin (€)': cat_total - cat_cost
                })
                
                # Aggregate WBE data
                wbe_key = wbe or 'Unassigned'
                if wbe_key not in wbe_data:
                    wbe_data[wbe_key] = {'total': 0, 'cost': 0, 'categories': 0, 'items': 0}
                
                wbe_data[wbe_key]['total'] += cat_total
                wbe_data[wbe_key]['cost'] += cat_cost
                wbe_data[wbe_key]['categories'] += 1
                wbe_data[wbe_key]['items'] += len(category.get('items', []))
        
        # WBE Summary Table
        self.story.append(Paragraph("5.1 WBE Summary", self.styles['CustomHeading2']))
        
        if wbe_data:
            wbe_table_data = [['WBE', 'Categories', 'Items', 'Total (€)', 'Cost (€)', 'Margin (€)', 'Margin (%)']]
            
            for wbe, data in sorted(wbe_data.items()):
                margin = data['total'] - data['cost']
                margin_perc = (margin / data['total'] * 100) if data['total'] > 0 else 0
                
                wbe_table_data.append([
                    wbe[:15] + '...' if len(wbe) > 15 else wbe,
                    f"{data['categories']:,}",
                    f"{data['items']:,}",
                    f"€{data['total']:,.0f}",
                    f"€{data['cost']:,.0f}",
                    f"€{margin:,.0f}",
                    f"{margin_perc:.1f}%"
                ])
            
            wbe_table = Table(wbe_table_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
            wbe_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            self.story.append(wbe_table)
            self.story.append(Spacer(1, 20))
            
            # WBE Distribution Chart using reliable method
            try:
                # Prepare chart data
                chart_data = [
                    {'WBE': wbe[:15], 'Total': data['total'], 'Cost': data['cost']}
                    for wbe, data in wbe_data.items()
                ]
                
                if chart_data and len(chart_data) <= 10:  # Reasonable limit for bar chart readability
                    self.logger.debug("Creating WBE distribution bar chart...")
                    chart_path = self._create_chart_image_reliable(
                        chart_data, 'bar', 'WBE', 'Total', 
                        'WBE Cost Distribution', 'wbe_distribution.png'
                    )
                    
                    if chart_path and os.path.exists(chart_path):
                        self.story.append(Image(chart_path, width=6*inch, height=3*inch))
                        self.logger.info("WBE chart added successfully")
                    else:
                        self.logger.info("WBE chart creation skipped - continuing without chart")
                else:
                    self.logger.info(f"Too many WBEs for chart ({len(chart_data)}), skipping for readability")
                    
            except Exception as e:
                self.logger.warning(f"WBE chart creation failed: {str(e)} - continuing without chart")
        
        else:
            self.story.append(Paragraph("No WBE data available in this file.", self.styles['CustomNormal']))
        
        self.story.append(PageBreak())
    
    def _add_profitability_analysis(self):
        """Add profitability analysis section"""
        self.story.append(Paragraph("6. Profitability Analysis", self.styles['CustomHeading1']))
        
        totals = self.data.get('totals', {})
        
        # Overall profitability metrics
        total_listino = self._safe_float(totals.get('total_pricelist', 0))
        total_cost = self._safe_float(totals.get('total_cost', 0))
        total_offer = self._safe_float(totals.get('total_offer', 0))
        
        listino_margin = total_listino - total_cost
        listino_margin_perc = (listino_margin / total_listino * 100) if total_listino > 0 else 0
        
        profitability_text = f"""
        <b>Overall Profitability Analysis:</b><br/><br/>
        
        <b>Based on Listino Prices:</b><br/>
        • Total Listino Value: €{total_listino:,.2f}<br/>
        • Total Cost: €{total_cost:,.2f}<br/>
        • Listino Margin: €{listino_margin:,.2f}<br/>
        • Listino Margin %: {listino_margin_perc:.1f}%<br/><br/>
        """
        
        if total_offer > 0:
            offer_margin = total_offer - total_cost
            offer_margin_perc = (offer_margin / total_offer * 100) if total_offer > 0 else 0
            
            profitability_text += f"""
            <b>Based on Offer Prices:</b><br/>
            • Total Offer Value: €{total_offer:,.2f}<br/>
            • Offer Margin: €{offer_margin:,.2f}<br/>
            • Offer Margin %: {offer_margin_perc:.1f}%<br/><br/>
            """
        
        # Add profitability assessment
        if listino_margin_perc > 30:
            assessment = "Excellent profitability"
        elif listino_margin_perc > 20:
            assessment = "Good profitability"
        elif listino_margin_perc > 10:
            assessment = "Moderate profitability"
        else:
            assessment = "Low profitability - review required"
            
        profitability_text += f"<b>Assessment:</b> {assessment}"
        
        self.story.append(Paragraph(profitability_text, self.styles['ExecutiveSummary']))
        
        # Profitability by group
        self.story.append(Paragraph("6.1 Profitability by Group", self.styles['CustomHeading2']))
        
        group_profitability = []
        for group in self.data.get('product_groups', []):
            categories = group.get('categories', [])
            
            if self.file_type == 'analisi_profittabilita':
                group_total = sum(self._safe_float(cat.get('pricelist_subtotal', 0)) for cat in categories)
                group_cost = sum(self._safe_float(cat.get('cost_subtotal', 0)) for cat in categories)
            else:
                group_total = sum(self._safe_float(item.get('pricelist_total_price', 0)) 
                                for cat in categories for item in cat.get('items', []))
                group_cost = sum(self._safe_float(item.get('total_cost', 0)) 
                               for cat in categories for item in cat.get('items', []))
            
            group_margin = group_total - group_cost
            group_margin_perc = (group_margin / group_total * 100) if group_total > 0 else 0
            
            group_profitability.append({
                'Group': group.get('group_id', 'Unknown'),
                'Total': group_total,
                'Cost': group_cost,
                'Margin': group_margin,
                'Margin %': group_margin_perc
            })
        
        # Profitability table
        prof_table_data = [['Group', 'Total (€)', 'Cost (€)', 'Margin (€)', 'Margin (%)']]
        for group in group_profitability:
            prof_table_data.append([
                group['Group'],
                f"€{group['Total']:,.0f}",
                f"€{group['Cost']:,.0f}",
                f"€{group['Margin']:,.0f}",
                f"{group['Margin %']:.1f}%"
            ])
        
        prof_table = Table(prof_table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        prof_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(prof_table)
        self.story.append(PageBreak())
    
    def _add_cost_distribution_analysis(self):
        """Add cost distribution analysis"""
        self.story.append(Paragraph("7. Cost Distribution Analysis", self.styles['CustomHeading1']))
        
        # Analyze cost distribution across departments/WBEs
        cost_distribution = {}
        
        for group in self.data.get('product_groups', []):
            for category in group.get('categories', []):
                wbe = category.get('wbe', '').strip() or 'Unassigned'
                
                if self.file_type == 'analisi_profittabilita':
                    cat_cost = self._safe_float(category.get('cost_subtotal', 0))
                else:
                    cat_cost = sum(self._safe_float(item.get('total_cost', 0)) for item in category.get('items', []))
                
                if wbe not in cost_distribution:
                    cost_distribution[wbe] = 0
                cost_distribution[wbe] += cat_cost
        
        if cost_distribution:
            total_cost = sum(cost_distribution.values())
            
            cost_text = f"""
            <b>Cost Distribution Analysis:</b><br/><br/>
            
            This analysis shows how project costs are distributed across different Work Breakdown Elements (WBEs) 
            or departments. Understanding this distribution helps in resource allocation and project management.<br/><br/>
            
            <b>Total Project Cost: €{total_cost:,.2f}</b><br/><br/>
            """
            
            self.story.append(Paragraph(cost_text, self.styles['CustomNormal']))
            
            # Cost distribution table
            cost_table_data = [['WBE/Department', 'Cost (€)', 'Percentage', 'Cumulative %']]
            
            # Sort by cost descending
            sorted_costs = sorted(cost_distribution.items(), key=lambda x: x[1], reverse=True)
            cumulative = 0
            
            for wbe, cost in sorted_costs:
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                cumulative += percentage
                
                cost_table_data.append([
                    wbe[:20] + '...' if len(wbe) > 20 else wbe,
                    f"€{cost:,.0f}",
                    f"{percentage:.1f}%",
                    f"{cumulative:.1f}%"
                ])
            
            cost_table = Table(cost_table_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            self.story.append(cost_table)
            self.story.append(Spacer(1, 20))
            
            # Cost distribution pie chart using reliable method
            try:
                # Prepare chart data
                chart_data = [
                    {'WBE': wbe[:15], 'Cost': cost}
                    for wbe, cost in sorted_costs
                ]
                
                if chart_data and len(chart_data) <= 12:  # Reasonable limit for pie chart readability
                    self.logger.debug("Creating cost distribution pie chart...")
                    chart_path = self._create_chart_image_reliable(
                        chart_data, 'pie', 'WBE', 'Cost', 
                        'Cost Distribution by WBE/Department', 'cost_distribution.png'
                    )
                    
                    if chart_path and os.path.exists(chart_path):
                        self.story.append(Image(chart_path, width=6*inch, height=3*inch))
                        self.logger.info("Cost distribution chart added successfully")
                    else:
                        self.logger.info("Cost chart creation skipped - continuing without chart")
                else:
                    self.logger.info(f"Too many cost centers for chart ({len(chart_data)}), skipping for readability")
                    
            except Exception as e:
                self.logger.warning(f"Cost chart creation failed: {str(e)} - continuing without chart")
        
        self.story.append(PageBreak())
    
    def _add_recommendations(self):
        """Add recommendations section"""
        self.story.append(Paragraph("9. Recommendations", self.styles['CustomHeading1']))
        
        totals = self.data.get('totals', {})
        total_listino = self._safe_float(totals.get('total_pricelist', 0))
        total_cost = self._safe_float(totals.get('total_cost', 0))
        margin_perc = ((total_listino - total_cost) / total_listino * 100) if total_listino > 0 else 0
        
        recommendations = []
        
        # Margin-based recommendations
        if margin_perc < 10:
            recommendations.append("• <b>Critical:</b> Margin is below 10%. Review cost structure and pricing strategy.")
        elif margin_perc < 20:
            recommendations.append("• <b>Caution:</b> Margin is below 20%. Consider cost optimization opportunities.")
        elif margin_perc > 40:
            recommendations.append("• <b>Opportunity:</b> High margin suggests potential for competitive pricing or additional investment.")
        
        # WBE-based recommendations
        if self.file_type == 'analisi_profittabilita':
            wbe_count = self._count_wbes()
            if wbe_count == 0:
                recommendations.append("• <b>Process:</b> Consider implementing WBE classification for better cost tracking.")
            elif wbe_count > 10:
                recommendations.append("• <b>Process:</b> Large number of WBEs detected. Consider consolidation for better management.")
        
        # Structure-based recommendations
        total_groups = len(self.data.get('product_groups', []))
        total_items = sum(len(cat.get('items', [])) for group in self.data.get('product_groups', []) for cat in group.get('categories', []))
        
        if total_items > 1000:
            recommendations.append("• <b>Complexity:</b> Large number of items. Consider grouping strategies for better management.")
        
        if total_groups > 20:
            recommendations.append("• <b>Structure:</b> Consider consolidating product groups for clearer project organization.")
        
        # General recommendations
        recommendations.extend([
            "• <b>Monitoring:</b> Implement regular cost tracking and variance analysis.",
            "• <b>Documentation:</b> Maintain detailed records of cost assumptions and changes.",
            "• <b>Review:</b> Schedule periodic reviews of project structure and cost allocation.",
        ])
        
        recommendations_text = "<br/>".join(recommendations)
        
        self.story.append(Paragraph("Based on the analysis of this project structure, the following recommendations are suggested:", self.styles['CustomNormal']))
        self.story.append(Spacer(1, 10))
        self.story.append(Paragraph(recommendations_text, self.styles['CustomNormal']))
        
        # Add footer with generation timestamp
        self.story.append(Spacer(1, 30))
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.story.append(Paragraph(footer_text, self.styles['CustomNormal']))
    
    def generate_pdf_report(self, progress_callback=None) -> Optional[BytesIO]:
        """Generate comprehensive PDF report"""
        
        if not REPORTLAB_AVAILABLE:
            st.error("ReportLab is required for PDF generation. Please install: pip install reportlab")
            return None
        
        try:
            self.logger.info("Starting PDF report generation")
            
            # Setup
            if progress_callback:
                progress_callback(5, "Initializing PDF generation...")
            
            self.logger.info("Setting up styles...")
            self._setup_styles()
            buffer = BytesIO()
            
            if progress_callback:
                progress_callback(10, "Creating PDF document...")
            
            # Create document
            self.logger.info("Creating PDF document structure...")
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
                title="Project Structure Analysis Report"
            )
            
            # Build content with detailed progress
            if progress_callback:
                progress_callback(15, "Adding table of contents...")
            self.logger.info("Adding table of contents...")
            self._add_table_of_contents()
            
            if progress_callback:
                progress_callback(25, "Adding executive summary...")
            self.logger.info("Adding executive summary...")
            self._add_executive_summary()
            
            if progress_callback:
                progress_callback(35, "Adding project overview...")
            self.logger.info("Adding project overview...")
            self._add_project_overview()
            
            if progress_callback:
                progress_callback(45, "Adding group analysis - processing groups...")
            self.logger.info("Starting group analysis...")
            self._add_group_analysis()
            self.logger.info("Group analysis completed")
            
            if progress_callback:
                progress_callback(55, "Adding WBE analysis - processing categories...")
            self.logger.info("Starting WBE analysis...")
            self._add_category_wbe_analysis()
            self.logger.info("WBE analysis completed")
            
            if progress_callback:
                progress_callback(65, "Adding profitability analysis...")
            self.logger.info("Starting profitability analysis...")
            self._add_profitability_analysis()
            self.logger.info("Profitability analysis completed")
            
            if progress_callback:
                progress_callback(75, "Adding cost distribution analysis...")
            self.logger.info("Starting cost distribution analysis...")
            self._add_cost_distribution_analysis()
            self.logger.info("Cost distribution analysis completed")
            
            if progress_callback:
                progress_callback(85, "Adding recommendations...")
            self.logger.info("Adding recommendations...")
            self._add_recommendations()
            
            if progress_callback:
                progress_callback(90, "Building PDF document - creating final file...")
            
            # Build PDF
            self.logger.info("Building final PDF document...")
            doc.build(self.story)
            buffer.seek(0)
            
            if progress_callback:
                progress_callback(95, "Finalizing PDF...")
            
            self.logger.info("PDF generation completed successfully")
            
            if progress_callback:
                progress_callback(100, "PDF generation completed!")
            
            return buffer
            
        except Exception as e:
            error_msg = f"Error generating PDF report: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            st.error(error_msg)
            st.error(f"Details: {traceback.format_exc()}")
            return None
        
        finally:
            # Cleanup temporary files
            self.logger.info("Cleaning up temporary files...")
            self._cleanup_temp_files()


def render_pdf_export_button(data: Dict[str, Any], file_type: str = None):
    """Render PDF export button in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 PDF Report")
    
    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("🔍 Debug Mode", help="Show detailed logs during PDF generation")
    
    # Chart options
    skip_charts = st.sidebar.checkbox("⚡ Skip Charts (Faster)", value=False, 
                                     help="Skip chart generation for faster PDF creation")
    
    # Add help message about potential issues
    with st.sidebar.expander("ℹ️ PDF Generation Help", expanded=False):
        st.markdown("""
        **If PDF generation gets stuck:**
        1. Enable Debug Mode to see detailed progress
        2. Check "Skip Charts" for faster generation
        3. Check for large datasets (>1000 items may be slow)
        4. Try with a smaller dataset first
        
        **Generation typically takes:**
        • With charts: 30-120 seconds
        • Without charts: 10-30 seconds
        """)
    
    if st.sidebar.button("📊 Generate Comprehensive PDF Report", type="primary", use_container_width=True):
        
        # Show progress
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        # Debug output area
        debug_container = st.sidebar.empty()
        debug_messages = []
        
        def update_progress(percent, message):
            progress_bar.progress(percent)
            status_text.text(message)
            
            if debug_mode:
                debug_messages.append(f"{percent}%: {message}")
                # Keep only last 5 messages
                if len(debug_messages) > 5:
                    debug_messages.pop(0)
                debug_container.text("\n".join(debug_messages))
        
        try:
            # Data validation before starting
            update_progress(0, "Validating data structure...")
            
            if not data:
                st.sidebar.error("❌ No data available for PDF generation")
                return
            
            if not data.get('product_groups'):
                st.sidebar.warning("⚠️ No product groups found in data")
            
            product_groups_count = len(data.get('product_groups', []))
            update_progress(2, f"Found {product_groups_count} product groups")
            
            # Set chart skipping environment variable if requested
            if skip_charts:
                os.environ['SKIP_PDF_CHARTS'] = 'true'
                update_progress(3, "Charts disabled - faster generation mode")
            else:
                os.environ.pop('SKIP_PDF_CHARTS', None)  # Remove if set
            
            # Generate PDF
            generator = ProjectStructurePDFGenerator(data, file_type)
            
            # Show data summary in debug mode
            if debug_mode:
                totals = data.get('totals', {})
                st.sidebar.info(f"""
                📊 Data Summary:
                • Groups: {product_groups_count}
                • Total Value: €{generator._safe_float(totals.get('total_pricelist', 0)):,.0f}
                • File Type: {file_type or 'auto-detect'}
                • Charts: {'Disabled' if skip_charts else 'Enabled'}
                """)
            
            pdf_buffer = generator.generate_pdf_report(progress_callback=update_progress)
            
            if pdf_buffer:
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                if debug_mode:
                    debug_container.empty()
                
                # Success message
                st.sidebar.success("✅ PDF report generated successfully!")
                
                # Download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                project_id = data.get('project', {}).get('id', 'unknown')
                filename = f"project_structure_report_{project_id}_{timestamp}.pdf"
                
                st.sidebar.download_button(
                    label="💾 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Report info
                st.sidebar.info(f"📋 Report includes:\n• Executive Summary\n• Project Overview\n• Group Analysis\n• WBE Distribution\n• Profitability Analysis\n• Cost Distribution\n• Recommendations")
                
            else:
                progress_bar.empty()
                status_text.empty()
                if debug_mode:
                    debug_container.empty()
                st.sidebar.error("❌ Failed to generate PDF report - check logs above")
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            if debug_mode:
                debug_container.empty()
            
            st.sidebar.error(f"❌ Error during PDF generation: {str(e)}")
            
            if debug_mode:
                st.sidebar.code(f"Error details:\n{traceback.format_exc()}", language="text") 