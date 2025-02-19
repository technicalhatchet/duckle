from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QComboBox, QTreeWidget, QTreeWidgetItem,
                             QScrollArea, QLineEdit, QMessageBox, QFileDialog, QStyleFactory)
from PyQt5.QtCore import Qt, QSize, QDateTime
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
import sys
import pandas as pd
from datetime import datetime

class DarkTheme:
    # Color scheme remains the same
    PRIMARY_DARK = "#1e1e1e"
    SECONDARY_DARK = "#252526"
    ACCENT_BLUE = "#264F78"
    ACCENT_GREEN = "#2D5A27"
    ACCENT_ORANGE = "#CE9178"
    TEXT_WHITE = "#FFFFFF"
    TEXT_GRAY = "#CCCCCC"

    @staticmethod
    def apply(app):
        # Theme application remains the same
        app.setStyle(QStyleFactory.create("Fusion"))

        dark_palette = QPalette()

        dark_palette.setColor(QPalette.Window, QColor(DarkTheme.PRIMARY_DARK))
        dark_palette.setColor(QPalette.WindowText, QColor(DarkTheme.TEXT_WHITE))
        dark_palette.setColor(QPalette.Base, QColor(DarkTheme.SECONDARY_DARK))
        dark_palette.setColor(QPalette.AlternateBase, QColor(DarkTheme.PRIMARY_DARK))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(DarkTheme.TEXT_WHITE))
        dark_palette.setColor(QPalette.ToolTipText, QColor(DarkTheme.TEXT_WHITE))
        dark_palette.setColor(QPalette.Text, QColor(DarkTheme.TEXT_WHITE))
        dark_palette.setColor(QPalette.Button, QColor(DarkTheme.SECONDARY_DARK))
        dark_palette.setColor(QPalette.ButtonText, QColor(DarkTheme.TEXT_WHITE))
        dark_palette.setColor(QPalette.Link, QColor(DarkTheme.ACCENT_BLUE))
        dark_palette.setColor(QPalette.Highlight, QColor(DarkTheme.ACCENT_BLUE))
        dark_palette.setColor(QPalette.HighlightedText, QColor(DarkTheme.TEXT_WHITE))

        app.setPalette(dark_palette)

        # Stylesheet remains the same
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #FFFFFF;
            }
            
            QPushButton {
                background-color: #264F78;
                border: none;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
                font-size: 13px;
                min-width: 80px;
                height: 25px;
            }
            
            QPushButton:hover {
                background-color: #365F88;
            }
            
            QPushButton:pressed {
                background-color: #163F68;
            }
            
            QComboBox {
                background-color: #252526;
                border: 1px solid #363636;
                border-radius: 3px;
                padding: 5px;
                min-width: 200px;
                color: white;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            
            QTreeWidget {
                background-color: #252526;
                alternate-background-color: #2d2d2d;
                border: 1px solid #363636;
                color: white;
            }
            
            QTreeWidget::item {
                height: 25px;
            }
            
            QTreeWidget::item:selected {
                background-color: #264F78;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: white;
                padding: 5px;
                border: none;
            }
            
            QHeaderView::section:hover {
                background-color: #363636;
            }
            
            QLineEdit {
                background-color: #252526;
                border: 1px solid #363636;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
        """)

class SortableTreeWidgetItem(QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()

        # Get the text values for comparison
        text1 = self.text(column)
        text2 = other.text(column)

        # Date column (index 0)
        if column == 0:
            try:
                date1 = datetime.strptime(text1, "%Y-%m-%d")
                date2 = datetime.strptime(text2, "%Y-%m-%d")
                return date1 < date2
            except ValueError:
                return text1 < text2

        # Amount and Balance columns (indices 4 and 5)
        elif column in [4, 5]:
            try:
                # Remove any currency symbols and commas, then convert to float
                val1 = float(text1.replace('$', '').replace(',', ''))
                val2 = float(text2.replace('$', '').replace(',', ''))
                return val1 < val2
            except ValueError:
                return text1 < text2

        # Default string comparison for other columns
        return text1 < text2

class BudgetApp(QMainWindow):
    def __init__(self, file_handler, parser, db_handler):
        super().__init__()
        self.file_handler = file_handler
        self.parser = parser
        self.db_handler = db_handler
        self.current_sort_column = 0
        self.sort_order = Qt.AscendingOrder
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Duckle Budget Manager')
        self.setMinimumSize(1200, 800)

        # Set window icon
        self.setWindowIcon(QIcon('Duckle256.png'))

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Header section
        header_layout = QHBoxLayout()

        # Logo and title container
        logo_title_layout = QHBoxLayout()

        # Add logo
        logo_label = QLabel()
        logo_pixmap = QPixmap('Duckle256.png')
        scaled_pixmap = logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_title_layout.addWidget(logo_label)

        # Title
        title_label = QLabel('Duckle')
        title_label.setFont(QFont('Garamond', 24, QFont.Bold))
        header_layout.addWidget(title_label)

        # Button container
        button_layout = QHBoxLayout()

        # Create buttons
        self.load_pdf_btn = QPushButton('Load PDF')
        self.load_pdf_btn.clicked.connect(self.load_pdf)
        self.export_btn = QPushButton('Export')
        self.export_btn.clicked.connect(self.export_data)

        button_layout.addWidget(self.load_pdf_btn)
        button_layout.addWidget(self.export_btn)
        header_layout.addLayout(button_layout)

        layout.addLayout(header_layout)

        # Category section
        category_layout = QHBoxLayout()

        # Category dropdown
        self.category_combo = QComboBox()
        self.category_combo.addItems(list(self.parser.categorization_rules.keys()))

        self.set_category_btn = QPushButton('Set Category')
        self.set_category_btn.clicked.connect(self.set_category)

        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(self.set_category_btn)

        # New category section
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText('New Category')
        self.add_category_btn = QPushButton('Add Category')
        self.add_category_btn.clicked.connect(self.add_new_category)

        category_layout.addWidget(self.new_category_input)
        category_layout.addWidget(self.add_category_btn)
        category_layout.addStretch()

        layout.addLayout(category_layout)

        # Transaction tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            "Date", "Type", "Transaction Type", "Details",
            "Amount", "Balance", "Category", "Subcategory"
        ])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnCount(8)

        # Enable sorting
        self.tree.setSortingEnabled(True)
        self.tree.header().setSectionsClickable(True)
        self.tree.header().sectionClicked.connect(self.handle_sort)

        # Set column widths
        self.tree.setColumnWidth(0, 100)  # Date
        self.tree.setColumnWidth(1, 100)  # Type
        self.tree.setColumnWidth(2, 120)  # Transaction Type
        self.tree.setColumnWidth(3, 300)  # Details
        self.tree.setColumnWidth(4, 100)  # Amount
        self.tree.setColumnWidth(5, 100)  # Balance
        self.tree.setColumnWidth(6, 100)  # Category
        self.tree.setColumnWidth(7, 100)  # Subcategory

        layout.addWidget(self.tree)

    def handle_sort(self, column):
        """Handle column sorting when header is clicked."""
        if self.current_sort_column == column:
            # Toggle sort order if same column is clicked
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            # Default to ascending order for new column
            self.sort_order = Qt.AscendingOrder
            self.current_sort_column = column

        self.tree.sortItems(column, self.sort_order)

    def load_pdf(self):
        """Handle PDF loading and transaction parsing."""
        text = self.file_handler.load_pdf()

        if not text:
            QMessageBox.critical(self, "Error", "No valid text was extracted from the PDF.")
            return

        transactions = self.parser.parse_bank_statement_with_year(text)

        if not transactions:
            QMessageBox.warning(self, "Warning", "No transactions were found in the PDF.")
            return

        # Insert transactions into database
        for transaction in transactions:
            self.db_handler.insert_transaction(transaction)

        self.populate_tree(transactions)

    def populate_tree(self, transactions):
        """Display transactions in the tree widget."""
        self.tree.clear()

        for transaction in transactions:
            item = SortableTreeWidgetItem(self.tree)

            # Format amount and balance with 2 decimal places
            amount = f"{transaction[4]:.2f}"
            balance = f"{transaction[5]:.2f}"

            # Set values for each column
            values = [
                transaction[0],  # Date
                transaction[1],  # Type
                transaction[2],  # Transaction Type
                transaction[3],  # Details
                amount,         # Amount
                balance,        # Balance
                transaction[6], # Category
                transaction[7]  # Subcategory
            ]

            for i, value in enumerate(values):
                item.setText(i, str(value))

            # Color coding for deposits/withdrawals
            if transaction[1] == "Deposit":
                item.setForeground(4, QColor(DarkTheme.ACCENT_GREEN))
            else:
                item.setForeground(4, QColor(DarkTheme.ACCENT_ORANGE))

        # Sort by current column and order
        self.tree.sortItems(self.current_sort_column, self.sort_order)

    def set_category(self):
        """Set category for selected transactions."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a transaction.")
            return

        category = self.category_combo.currentText()

        for item in selected_items:
            item.setText(6, category)  # Category column
            item.setText(7, category)  # Subcategory column

    def add_new_category(self):
        """Add a new category to the system."""
        new_category = self.new_category_input.text().strip()
        if not new_category:
            QMessageBox.warning(self, "Invalid", "Please enter a category name.")
            return

        if new_category in self.parser.categorization_rules:
            QMessageBox.warning(self, "Invalid", "Category already exists.")
            return

        self.parser.categorization_rules[new_category] = []
        self.category_combo.addItem(new_category)
        self.new_category_input.clear()
        QMessageBox.information(self, "Success", f"Category '{new_category}' added!")

    def export_data(self):
        """Export transaction data to CSV."""
        if self.tree.topLevelItemCount() == 0:
            QMessageBox.warning(self, "No Data", "No data to export.")
            return

        try:
            data = []
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                row = [item.text(j) for j in range(self.tree.columnCount())]
                data.append(row)

            df = pd.DataFrame(data, columns=[
                self.tree.headerItem().text(i)
                for i in range(self.tree.columnCount())
            ])

            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export Data", "", "CSV Files (*.csv)"
            )

            if file_name:
                df.to_csv(file_name, index=False)
                QMessageBox.information(
                    self, "Export Successful",
                    f"Data exported to {file_name}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting data: {str(e)}")

def main():
    app = QApplication(sys.argv)

    # Apply dark theme
    DarkTheme.apply(app)

    # Initialize handlers and parser
    from duckle_parser import BankStatementParser
    from database_handler import DatabaseHandler
    from file_handler import FileHandler

    parser = BankStatementParser()
    db_handler = DatabaseHandler()
    file_handler = FileHandler(parser, db_handler)

    # Create and show the main window
    window = BudgetApp(file_handler, parser, db_handler)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()