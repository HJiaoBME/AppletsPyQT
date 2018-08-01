import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from CODER_V3_py import Ui_Form
import cv2
import qrcode
from pystrich.code128 import Code128Encoder
import os


class Pyqt5_Serial(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("测试程序")
        self.ser = serial.Serial()
        self.port_check()

        # 接收数据和发送数据数目置零
        # self.data_num_received = 0
        # self.lineEdit.setText(str(self.data_num_received))
        # self.data_num_sended = 0
        # self.lineEdit_2.setText(str(self.data_num_sended))

    def init(self):
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        # 打开按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭按钮
        self.close_button.clicked.connect(self.port_close)

        # 发送数据按钮
        self.s3__send_button.clicked.connect(self.data_send)

        #
        self.push_Code128.clicked.connect(self.push_Code128_click)

        # 打开摄像头按钮
        self.open_btn_cam.clicked.connect(self.label_show_camera_click)

        # 关闭摄像头按钮
        self.close_btn_cam.clicked.connect(self.label_close_cam_click)

        # 检测摄像头
        self.detecBtn.clicked.connect(self.label_show_detection)
        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)

        #
        # self.digital_detect.clicked.connect(self.label_show_detection)

        # 初始化变量
        self.mac = []
        self.rssi = []
        self.numD = 0
        self.left_top = 0
        self.right_bottom = 0

        #
        self.textTH.setText('-45')
        self.textNum.setText(str(self.numD))


        # 初始化摄像头 图片label
        self.timer_camera = QTimer()
        self.timer_camera.timeout.connect(self.show_camera)
        self.label_show_camera.setScaledContents(True)
        self.label_show_result.setScaledContents(True)
        self.label_show_QR.setScaledContents(True)
        self.label_show_Code128.setScaledContents(True)
        self.cap = cv2.VideoCapture()
        self.cap_num = 0
        self.detect_flag = 0

        # inti OCR id
        # APP_ID = '11538066 '
        # API_KEY = 'hxVp4TcBnz3tIASyrpilOaG4'
        # SECRET_KEY = 'AVw6mlDK8fbF5pymzmnFh0SwUfvTUksI'

        #
        # APP_ID = '11541697'
        # API_KEY = 'Pke9usA5IinrrKnt44HGkMeT'
        # SECRET_KEY = 'DhKPmmvXfHxsTp7i06Ydy9GjdyxpP0Ga'

        if os.path.exists('OCR.txt'):
            f = open("OCR.txt", "r")  # 设置文件对象
            self.APP_ID = f.readline().strip('\n')
            self.API_KEY = f.readline().strip('\n')
            self.SECRET_KEY = f.readline().strip('\n')
            f.close()
        else :
            self.APP_ID = '11541697'
            self.API_KEY = 'Pke9usA5IinrrKnt44HGkMeT'
            self.SECRET_KEY = 'DhKPmmvXfHxsTp7i06Ydy9GjdyxpP0Ga'


    def push_Code128_click(self):
        data = self.text_code128.toPlainText()
        if data:
            encoder = Code128Encoder(data)
            encoder.save("code128.png")

            code128 = QtGui.QPixmap('code128.png')
            self.label_show_Code128.setPixmap(code128)

            # code128 = cv2.imread("code128.png")
            # code128 = cv2.resize(code128, (420, 150))
            # Coderimage = QtGui.QImage(code128.data, code128.shape[1], code128.shape[0], QtGui.QImage.Format_RGB888)
            # self.label_show_Code128.setPixmap(QtGui.QPixmap.fromImage(Coderimage))

    # 摄像头
    def label_show_camera_click(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.cap_num)
            if flag == False:
                msg = QMessageBox.warning(u"Warning", u"请检测相机与电脑是否连接正确", buttons=QMessageBox.Ok,
                                          defaultButton=QMessageBox.Ok)
            else:
                self.timer_camera.start(30)
                self.label_cap.setText("摄像头已连接")


    def label_close_cam_click(self):
        try:
            self.timer_camera.stop()
            self.cap.release()
        except:
            pass
        self.label_show_camera.clear()
        self.label_cap.setText("摄像头未连接")

    # 显示摄像头图片
    def show_camera(self):
        ret, frame = self.cap.read()
        show = cv2.resize(frame, (640, 480))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        self.left_top, self.right_bottom = self.coord_detection(show)

        cv2.rectangle(show, self.left_top, self.right_bottom, (255, 0, 0), 2)

        self.left_cut = -40
        self.top_cut = -120
        self.rigth_cut = 20
        self.bottom_cut = 190

        cv2.rectangle(show, (self.left_top[0] + self.left_cut, self.left_top[1] + self.top_cut), (self.right_bottom[0] - self.rigth_cut , self.right_bottom[1] - self.bottom_cut),
                      (0, 255, 0), 2)

        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)

        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))


    # 检测
    def label_show_detection(self):
        ret, frame = self.cap.read()
        self.timer_camera.stop()
        show_1 = cv2.resize(frame, (640, 480))
        cv2.imwrite('show.jpg', show_1)
        # show_1 = cv2.cvtColor(show_1, cv2.COLOR_BGR2RGB)


        # 识别文字
        cut_image = show_1[self.left_top[1] + self.top_cut:self.right_bottom[1] - self.bottom_cut, self.left_top[0] + self.left_cut:self.right_bottom[0] - self.rigth_cut]
        cut_image  = cv2.cvtColor(cut_image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('cut_img.png', cut_image)

        equ = cv2.equalizeHist(cut_image)

        cv2.imwrite('cut_img1.png', equ)
        # cccc = cv2.imread('cut_img.jpg')
        # cutImage = QtGui.QImage(cccc.data, cccc.shape[1], cccc.shape[0], QtGui.QImage.Format_RGB888)
        # self.label_show_result.setPixmap(QtGui.QPixmap.fromImage(cutImage))
        #
        cutImage = QtGui.QPixmap('cut_img.png')
        self.label_show_result.setPixmap(cutImage)


        words_str = self.read_word('cut_img.png')

        # words_str = 'MC20180601054'
        if words_str:
            self.text_code128.setText(words_str)
            encoder = Code128Encoder(words_str)
            encoder.save("code128.png")

            # code128 = cv2.imread("code128.png")
            # code128 = cv2.resize(code128, (420, 150))
            # Coderimage = QtGui.QImage(code128.data, code128.shape[1], code128.shape[0], QtGui.QImage.Format_RGB888)
            # self.label_show_Code128.setPixmap(QtGui.QPixmap.fromImage(Coderimage))

            code128 = QtGui.QPixmap('code128.png')
            self.label_show_Code128.setPixmap(code128)
        else :
            self.text_code128.setText('请手动输入')
            self.label_show_result.clear()

    # 画绿色框
    def coord_detection(self, rgb_img):
        gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        # 二维码的模板
        refer_img = cv2.imread('ref.png', 0)
        w, h = refer_img.shape[::-1]
        res = cv2.matchTemplate(gray_img, refer_img, cv2.TM_CCOEFF_NORMED)
        # threshold = 0.9
        # coord = np.where(res >= threshold)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        left_top = max_loc  # 左上角
        right_bottom = (left_top[0] + w, left_top[1] + h)  # 右下角
        return left_top, right_bottom

    def read_word(self, cut_img):
        # cut_img 是需要识别文字的图片
        from aip import AipOcr
        """ 你的 APPID AK SK """

        # APP_ID = '11538066 '
        # API_KEY = 'hxVp4TcBnz3tIASyrpilOaG4'
        # SECRET_KEY = 'AVw6mlDK8fbF5pymzmnFh0SwUfvTUksI'

        #
        # APP_ID = '11541697'
        # API_KEY = 'Pke9usA5IinrrKnt44HGkMeT'
        # SECRET_KEY = 'DhKPmmvXfHxsTp7i06Ydy9GjdyxpP0Ga'

        client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        with open(cut_img, 'rb') as f:
            img = f.read()
            # msg = client.basicGeneral(img)
            try:
                msg = client.basicGeneral(img)
                words = ''
                result = ''
                for item in msg['words_result']:
                    words = words + item['words']
                tmp = 'MC'
                if tmp in words:
                    pos = words.index(tmp)
                    num_tmp = words[pos + 2:pos + 13]
                    if self.is_number(num_tmp) and len(num_tmp) == 11:
                        result = tmp + num_tmp
                elif 'm' in  words:
                    pos = words.index('m')
                    num_tmp = words[pos + 2:pos + 13]
                    if self.is_number(num_tmp) and len(num_tmp) == 11:
                        result = tmp + num_tmp
                elif 'c' in  words:
                    pos = words.index('c')
                    num_tmp = words[pos + 1:pos + 12]
                    if self.is_number(num_tmp) and len(num_tmp) == 11:
                        result = tmp + num_tmp
                elif '20' in  words:
                    pos = words.index('20')
                    num_tmp = words[pos :pos + 11]
                    if self.is_number(num_tmp) and len(num_tmp) == 11:
                        result = tmp + num_tmp
                return result
            except:
                result = "百度API调用次数已用完"
                return result
                # if 'num_tmp' not in vars():
                #     number = "没有识别"
                #     print(number)
                #     return number
                # else:
                #     if self.is_number(num_tmp) and len(num_tmp)==11:
                #         number = num_tmp
                #     return number

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False



    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = 115200
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        # self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(2)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.label_sp.setText("串口已连接")

        # if self.timer_camera.isActive() == False:
        #     flag = self.cap.open(self.cap_num)
        #     if flag == False:
        #         msg = QMessageBox.warning(u"Warning", u"请检测相机与电脑是否连接正确", buttons=QMessageBox.Ok,
        #                                   defaultButton=QMessageBox.Ok)
        #     else:
        #         self.timer_camera.start(30)
        #         self.label_cap.setText("摄像头已连接")
                # self.open_camera.setText(u'关闭摄像头')




    # 关闭串口
    def port_close(self):
        self.timer.stop()
        # self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.label_sp.setText("串口未连接")

        # try :
        #     self.timer_camera.stop()
        #     self.cap.release()
        # except:
        #     pass
        # self.label_show_camera.clear()
        # self.label_cap.setText("摄像头未连接")


    #  生成 二维码 和 条形码
    def data_send(self):
        if self.ser.isOpen():
            input_Hex = [85, 170, 161, 170]
            self.ser.write(input_Hex)

            self.timer = QTimer()  # 初始化一个定时器
            self.timer.timeout.connect(self.operate)  # 计时结束调用operate()方法

            self.timer.start(1500)  # 设置计时间隔并启动
            # self.label_show_detection()
        else:
            pass

    def MAC_RSSi_set(self,data):
        if ('mac' in data):
            self.numD = self.numD + 1
            self.mac.append(data[4:17])
            self.rssi.append(int(data[25:]))


    def MAC_RSSi_cal(self):

        if len(self.rssi):
            #
            maxV = max(self.rssi)
            th = int(self.textTH.toPlainText())

            if maxV > th:
                resultMac = self.mac[self.rssi.index(maxV)]
                resultMac = resultMac.upper()
                self.textMAC.setText(resultMac)
                QRimg = qrcode.make(resultMac)
                QRimg.save("QRcode.png")

                # QRimg1 = cv2.imread("QRcode.png")
                # QRimg1 = cv2.resize(QRimg1, (250, 250))
                # QRimage = QtGui.QImage(QRimg1.data, QRimg1.shape[1], QRimg1.shape[0], QtGui.QImage.Format_RGB888)
                # self.label_show_QR.setPixmap(QtGui.QPixmap.fromImage(QRimage))

                QRimg1 = QtGui.QPixmap('QRcode.png')
                self.label_show_QR.setPixmap(QRimg1)
                self.RSSiResult.setText(str(maxV))
            # self.textMAC.setText(str(th))
            else:
                self.RSSiResult.setText('')
                self.label_show_QR.clear()
                self.textMAC.setText('未找到设备')
        else :
            self.label_show_QR.clear()
            self.textMAC.setText('未找到设备')
        # 清除索引数 开始摄像 清除debug内容
        self.textNum.setText(str(self.numD))
        self.timer_camera.start()
        # self.s2__receive_text.setText('')

        self.mac = []
        self.rssi = []
        self.numD = 0

    def operate(self):
        # 具体操作
        input_Hex = [85, 170, 162, 170]
        self.ser.write(input_Hex)
        self.timer.stop()
        self.MAC_RSSi_cal()



    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.readline()
            data = data.decode('iso-8859-1')
            self.MAC_RSSi_set(data)

            self.s2__receive_text.insertPlainText(data)

            # 获取到text光标
            textCursor = self.s2__receive_text.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.s2__receive_text.setTextCursor(textCursor)
        else:
            pass

    def receive_data_clear(self):
        self.s2__receive_text.setText("")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
