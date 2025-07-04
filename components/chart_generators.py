"""
Alternative Chart Generation Module
Provides multiple chart generation strategies to avoid Kaleido/Plotly hanging issues
"""

import os
import tempfile
import logging
from typing import Optional, List, Dict, Any
from io import BytesIO

# Strategy 1: Matplotlib (most reliable)
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Strategy 2: ReportLab's built-in charts
try:
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib import colors
    from reportlab.graphics import renderPDF
    REPORTLAB_CHARTS_AVAILABLE = True
except ImportError:
    REPORTLAB_CHARTS_AVAILABLE = False


class ChartGenerator:
    """Multi-strategy chart generator with fallbacks"""
    
    def __init__(self):
        self.logger = logging.getLogger('ChartGenerator')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        
        self.temp_files = []
        
    def cleanup_temp_files(self):
        """Clean up temporary chart files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                self.logger.warning(f"Could not delete temp file {file_path}: {e}")
        self.temp_files = []
    
    def create_pie_chart(self, data: List[Dict], values_key: str, names_key: str, 
                        title: str = "", filename: str = "pie_chart.png") -> Optional[str]:
        """Create pie chart using the best available method"""
        
        if not data:
            self.logger.warning("No data provided for pie chart")
            return None
        
        # Try matplotlib first (most reliable)
        if MATPLOTLIB_AVAILABLE:
            return self._create_matplotlib_pie_chart(data, values_key, names_key, title, filename)
        
        # Fallback to ReportLab charts
        if REPORTLAB_CHARTS_AVAILABLE:
            return self._create_reportlab_pie_chart(data, values_key, names_key, title, filename)
        
        # Final fallback to simple text representation
        return self._create_text_chart(data, values_key, names_key, title, filename)
    
    def create_bar_chart(self, data: List[Dict], x_key: str, y_key: str, 
                        title: str = "", filename: str = "bar_chart.png") -> Optional[str]:
        """Create bar chart using the best available method"""
        
        if not data:
            self.logger.warning("No data provided for bar chart")
            return None
        
        # Try matplotlib first
        if MATPLOTLIB_AVAILABLE:
            return self._create_matplotlib_bar_chart(data, x_key, y_key, title, filename)
        
        # Fallback to ReportLab charts
        if REPORTLAB_CHARTS_AVAILABLE:
            return self._create_reportlab_bar_chart(data, x_key, y_key, title, filename)
        
        # Final fallback to text representation
        return self._create_text_chart(data, x_key, y_key, title, filename)
    
    def _create_matplotlib_pie_chart(self, data: List[Dict], values_key: str, names_key: str, 
                                    title: str, filename: str) -> Optional[str]:
        """Create pie chart using matplotlib"""
        try:
            self.logger.debug(f"Creating matplotlib pie chart: {filename}")
            
            # Extract data
            values = [float(item.get(values_key, 0)) for item in data]
            labels = [str(item.get(names_key, 'Unknown'))[:15] for item in data]  # Truncate long labels
            
            # Filter out zero values
            filtered_data = [(v, l) for v, l in zip(values, labels) if v > 0]
            if not filtered_data:
                self.logger.warning("No positive values for pie chart")
                return None
            
            values, labels = zip(*filtered_data)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Create pie chart with better colors
            colors_list = plt.cm.Set3(np.linspace(0, 1, len(values)))
            
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors_list
            )
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            for text in texts:
                text.set_fontsize(8)
            
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
            
            # Save to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            plt.savefig(temp_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)  # Important: close figure to free memory
            
            self.temp_files.append(temp_path)
            self.logger.debug(f"Matplotlib pie chart created: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error creating matplotlib pie chart: {e}")
            return None
    
    def _create_matplotlib_bar_chart(self, data: List[Dict], x_key: str, y_key: str, 
                                    title: str, filename: str) -> Optional[str]:
        """Create bar chart using matplotlib"""
        try:
            self.logger.debug(f"Creating matplotlib bar chart: {filename}")
            
            # Extract and prepare data
            x_values = [str(item.get(x_key, 'Unknown'))[:20] for item in data]  # Truncate long labels
            y_values = [float(item.get(y_key, 0)) for item in data]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create bar chart
            bars = ax.bar(x_values, y_values, color=plt.cm.Set2(np.linspace(0, 1, len(x_values))))
            
            # Add value labels on bars
            for bar, value in zip(bars, y_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(y_values)*0.01,
                       f'{value:,.0f}', ha='center', va='bottom', fontsize=8)
            
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
            ax.set_xlabel(x_key.replace('_', ' ').title(), fontsize=10)
            ax.set_ylabel(y_key.replace('_', ' ').title(), fontsize=10)
            
            # Rotate x-axis labels if needed
            plt.xticks(rotation=45, ha='right')
            
            # Add grid for readability
            ax.grid(True, alpha=0.3, axis='y')
            
            # Save to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            plt.savefig(temp_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            self.temp_files.append(temp_path)
            self.logger.debug(f"Matplotlib bar chart created: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error creating matplotlib bar chart: {e}")
            return None
    
    def _create_reportlab_pie_chart(self, data: List[Dict], values_key: str, names_key: str, 
                                   title: str, filename: str) -> Optional[str]:
        """Create pie chart using ReportLab's built-in charts"""
        try:
            self.logger.debug(f"Creating ReportLab pie chart: {filename}")
            
            # Extract data
            values = [float(item.get(values_key, 0)) for item in data if float(item.get(values_key, 0)) > 0]
            labels = [str(item.get(names_key, 'Unknown'))[:15] for item in data if float(item.get(values_key, 0)) > 0]
            
            if not values:
                return None
            
            # Create drawing
            drawing = Drawing(400, 300)
            
            # Create pie chart
            pie = Pie()
            pie.x = 50
            pie.y = 50
            pie.width = 200
            pie.height = 200
            pie.data = values
            pie.labels = labels
            pie.slices.strokeWidth = 0.5
            
            # Add colors
            for i, slice in enumerate(pie.slices):
                slice.fillColor = colors.toColor(f'hsl({i * 360 / len(values)}, 70%, 60%)')
            
            drawing.add(pie)
            
            # Save to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), filename.replace('.png', '.pdf'))
            renderPDF.drawToFile(drawing, temp_path)
            
            self.temp_files.append(temp_path)
            self.logger.debug(f"ReportLab pie chart created: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error creating ReportLab pie chart: {e}")
            return None
    
    def _create_reportlab_bar_chart(self, data: List[Dict], x_key: str, y_key: str, 
                                   title: str, filename: str) -> Optional[str]:
        """Create bar chart using ReportLab's built-in charts"""
        try:
            self.logger.debug(f"Creating ReportLab bar chart: {filename}")
            
            # Extract data
            y_values = [float(item.get(y_key, 0)) for item in data]
            x_labels = [str(item.get(x_key, 'Unknown'))[:15] for item in data]
            
            # Create drawing
            drawing = Drawing(500, 300)
            
            # Create bar chart
            bar_chart = VerticalBarChart()
            bar_chart.x = 50
            bar_chart.y = 50
            bar_chart.height = 200
            bar_chart.width = 400
            bar_chart.data = [y_values]
            bar_chart.categoryAxis.categoryNames = x_labels
            
            # Styling
            bar_chart.bars[0].fillColor = colors.lightblue
            bar_chart.valueAxis.valueMin = 0
            bar_chart.valueAxis.valueMax = max(y_values) * 1.1 if y_values else 100
            
            drawing.add(bar_chart)
            
            # Save to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), filename.replace('.png', '.pdf'))
            renderPDF.drawToFile(drawing, temp_path)
            
            self.temp_files.append(temp_path)
            self.logger.debug(f"ReportLab bar chart created: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error creating ReportLab bar chart: {e}")
            return None
    
    def _create_text_chart(self, data: List[Dict], key1: str, key2: str, 
                          title: str, filename: str) -> Optional[str]:
        """Create a simple text-based chart representation"""
        try:
            self.logger.debug(f"Creating text chart: {filename}")
            
            # Create a simple text file with chart data
            temp_path = os.path.join(tempfile.gettempdir(), filename.replace('.png', '.txt'))
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")
                f.write("=" * len(title) + "\n\n")
                
                for item in data:
                    name = str(item.get(key1, 'Unknown'))[:30]
                    value = float(item.get(key2, 0))
                    
                    # Simple bar representation
                    bar_length = int(value / max([float(d.get(key2, 1)) for d in data]) * 50) if data else 0
                    bar = "█" * bar_length
                    
                    f.write(f"{name:<30} {bar} {value:,.0f}\n")
            
            self.temp_files.append(temp_path)
            self.logger.debug(f"Text chart created: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error creating text chart: {e}")
            return None
    
    def get_chart_capabilities(self) -> Dict[str, bool]:
        """Return available chart generation capabilities"""
        return {
            "matplotlib": MATPLOTLIB_AVAILABLE,
            "reportlab_charts": REPORTLAB_CHARTS_AVAILABLE,
            "text_fallback": True
        }


# Utility function for easy access
def create_chart_generator():
    """Create and return a chart generator instance"""
    return ChartGenerator()


# Test function
def test_chart_generation():
    """Test chart generation capabilities"""
    print("🧪 Testing Chart Generation Capabilities")
    print("=" * 40)
    
    generator = ChartGenerator()
    capabilities = generator.get_chart_capabilities()
    
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"{status} {capability}")
    
    # Test data
    test_data = [
        {"name": "Group A", "value": 1000},
        {"name": "Group B", "value": 1500},
        {"name": "Group C", "value": 800}
    ]
    
    print(f"\n📊 Testing with sample data ({len(test_data)} items)")
    
    # Test pie chart
    pie_path = generator.create_pie_chart(test_data, "value", "name", "Test Distribution")
    if pie_path:
        print(f"✅ Pie chart created: {pie_path}")
    else:
        print("❌ Pie chart creation failed")
    
    # Test bar chart
    bar_path = generator.create_bar_chart(test_data, "name", "value", "Test Values")
    if bar_path:
        print(f"✅ Bar chart created: {bar_path}")
    else:
        print("❌ Bar chart creation failed")
    
    print(f"\n🧹 Cleaning up...")
    generator.cleanup_temp_files()
    print("✅ Cleanup completed")


if __name__ == "__main__":
    test_chart_generation() 