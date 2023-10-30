import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('QTableWidget Example')

        # QTableWidget 생성
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(50, 50, 300, 100)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Column 1", "Column 2"])

        # 테이블에 데이터 추가
        data = [["Row 1, Col 1", "Row 1, Col 2"],
                ["Row 2, Col 1", "Row 2, Col 2"],
                ["Row 3, Col 1", "Row 3, Col 2"]]
        self.tableWidget.setRowCount(len(data))
        for row, rowData in enumerate(data):
            for col, value in enumerate(rowData):
                item = QTableWidgetItem(value)
                self.tableWidget.setItem(row, col, item)

        # 삭제 버튼
        delete_button = QPushButton("Delete Selected Row", self)
        delete_button.setGeometry(50, 170, 150, 30)
        delete_button.clicked.connect(self.deleteSelectedRow)

    def deleteSelectedRow(self):
        selected_items = self.tableWidget.selectedItems()

        if selected_items:
            rows_to_remove = set()
            for item in selected_items:
                rows_to_remove.add(item.row())

            # 행 삭제
            for row in sorted(rows_to_remove, reverse=True):
                self.tableWidget.removeRow(row)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
