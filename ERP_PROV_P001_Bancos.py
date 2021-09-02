import sys
import time
from Funciones04 import *
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import urllib.request

sqlCod_Prov="SELECT Cod_prov,Nro_Correlativo FROM TAB_PROV_007_Bancos_y_cuentas_del_Proveedor"

sqlCod_Banco="SELECT Descrip_Banco,Cod_Banco FROM TAB_SOC_016_Tipo_de_Bancos"

sqlMoneda="SELECT Descrip_moneda,Cod_moneda FROM TAB_SOC_008_Monedas"

sqlUbigeo="SELECT * FROM TAB_SOC_009_Ubigeo ORDER BY Cod_Distrito ASC, Cod_Provincia ASC, Cod_Depart_Region ASC, Cod_Pais ASC"

class Bancos(QMainWindow):
    def __init__(self,codsoc,codusuario,Cod_Prov,Razon_Social):
        QMainWindow.__init__(self)
        uic.loadUi("ERP_PPROV_003.ui",self)

        global Cod_Soc,Cod_Usuario,TCta,sqlBanco,dicbanco,dicmoneda,datos
        global banco,mon

        Cod_Soc=codsoc
        Cod_Usuario=codusuario

        TCta={'Cuenta de Ahorro':'CA','Cuenta Corriente':'CC'}

        self.leCod_Prov.setText(Cod_Prov)
        self.leRazon_Social.setText(Razon_Social)
        self.leCod_Prov.setReadOnly(True)
        self.leRazon_Social.setReadOnly(True)
        self.pbModificar.setEnabled(False)

        self.tbwReg_Bancos_Cuentas_Prov.currentCellChanged.connect(self.AgregarFila)
        self.pbGrabar.clicked.connect(self.Grabar)
        self.pbModificar.clicked.connect(self.Modificar)
        self.pbHabilitar.clicked.connect(self.Habilitar)
        self.pbRetornar.clicked.connect(self.Salir)
        self.pbBaja.clicked.connect(self.Baja)

        cargarLogo(self.lbLogo_Mp,'multiplay')
        cargarLogo(self.lbLogo_Soc, Cod_Soc)
        cargarIcono(self, 'erp')
        cargarIcono(self.pbGrabar, 'grabar')
        cargarIcono(self.pbModificar, 'modificar')
        cargarIcono(self.pbHabilitar, 'habilitar')
        cargarIcono(self.pbBaja, 'darbaja')
        cargarIcono(self.pbRetornar, 'salir')

        banco=consultarSql(sqlCod_Banco)
        dicbanco={}
        for dato in banco:
            dicbanco[dato[1]]=dato[0]

        mon=consultarSql(sqlMoneda)
        dicmoneda={}
        for dato in mon:
            dicmoneda[dato[1]]=dato[0]

        Ubigeo=consultarSql(sqlUbigeo)
        datos={}
        for dato in Ubigeo:
            codigo="-".join(dato[0:4])
            if codigo not in datos:
                datos[codigo]=dato[4]

        sqlBanco="SELECT Nro_Correlativo,Pais,Departamento,Entidad_Bancaria,Tipo_cuenta,Cuenta_Banco,Moneda,Cuenta_Interbanco,Estado_Banco FROM TAB_PROV_007_Bancos_y_cuentas_del_Proveedor WHERE Cod_Prov='%s'" %(Cod_Prov)
        actualizarBan(self,self.tbwReg_Bancos_Cuentas_Prov,sqlBanco,datos,TCta,dicbanco,banco,dicmoneda,mon)

    def AgregarFila(self,fila,columna):
        if fila==self.tbwReg_Bancos_Cuentas_Prov.rowCount()-1:
            rowPosition = self.tbwReg_Bancos_Cuentas_Prov.rowCount()
            self.tbwReg_Bancos_Cuentas_Prov.insertRow(rowPosition)

            #item "Id" queda desactivada...
            id=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),0).text()
            flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            sigNro=int(id)+1
            Nro=QTableWidgetItem(str(sigNro))
            Nro.setFlags(flags)
            self.tbwReg_Bancos_Cuentas_Prov.setItem(rowPosition,0, Nro)

            #item "Estado" queda desactivada...
            # flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item=QTableWidgetItem()
            item.setFlags(flags)
            self.tbwReg_Bancos_Cuentas_Prov.setItem(rowPosition,8, item)
            # self.pbGrabar.setEnabled(False)

            #creacion combo pais...
            cb0 = QComboBox(self.tbwReg_Bancos_Cuentas_Prov)
            self.tbwReg_Bancos_Cuentas_Prov.setCellWidget(rowPosition, 1, cb0)
            for k,v in datos.items():
                codigo=k.split("-")
                if "-".join(codigo[1:])=="0-0-0":
                    cb0.addItem(v)
            cb0.setCurrentIndex(-1)
            # cb0.setStyleSheet("background-color: rgb(255,255,255);")
            font = QtGui.QFont()
            font.setPointSize(12)
            cb0.setFont(font)
            self.tbwReg_Bancos_Cuentas_Prov.resizeColumnToContents(1)
            cb0.activated.connect(self.cargarDepartamento)

            #creacion combo departamento...
            cb1 = QComboBox(self.tbwReg_Bancos_Cuentas_Prov)
            self.tbwReg_Bancos_Cuentas_Prov.setCellWidget(rowPosition, 2, cb1)
            cb1.setCurrentIndex(-1)
            # cb1.setStyleSheet("background-color: rgb(255,255,255);")
            font = QtGui.QFont()
            font.setPointSize(12)
            cb1.setFont(font)
            self.tbwReg_Bancos_Cuentas_Prov.resizeColumnToContents(2)

            #creacion combo tipo de banco...
            cb2 = QComboBox(self.tbwReg_Bancos_Cuentas_Prov)
            self.tbwReg_Bancos_Cuentas_Prov.setCellWidget(rowPosition, 3, cb2)
            insertarDatos(cb2,banco)
            cb2.setCurrentIndex(-1)
            # cb2.setStyleSheet("background-color: rgb(255,255,255);")
            font = QtGui.QFont()
            font.setPointSize(12)
            cb2.setFont(font)
            self.tbwReg_Bancos_Cuentas_Prov.resizeColumnToContents(3)

            #creacion combo tipo de cuenta...
            cb3 = QComboBox(self.tbwReg_Bancos_Cuentas_Prov)
            self.tbwReg_Bancos_Cuentas_Prov.setCellWidget(rowPosition, 4, cb3)
            for k,v in TCta.items():
                cb3.addItem(k)
            cb3.setCurrentIndex(-1)
            # cb3.setStyleSheet("background-color: rgb(255,255,255);")
            font = QtGui.QFont()
            font.setPointSize(12)
            cb3.setFont(font)
            self.tbwReg_Bancos_Cuentas_Prov.resizeColumnToContents(4)

            cb4 = QComboBox(self.tbwReg_Bancos_Cuentas_Prov)
            self.tbwReg_Bancos_Cuentas_Prov.setCellWidget(rowPosition, 6, cb4)
            insertarDatos(cb4,mon)
            cb4.setCurrentIndex(-1)
            # cb4.setStyleSheet("background-color: rgb(255,255,255);")
            font = QtGui.QFont()
            font.setPointSize(12)
            cb4.setFont(font)
            self.tbwReg_Bancos_Cuentas_Prov.resizeColumnToContents(6)

    def cargarDepartamento(self):
        pais=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 1).currentText()
        if pais=="": return
        self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 2).clear()
        for k,v in datos.items():
            codigoDep=k.split("-")
            if v==pais and "-".join(codigoDep[1:])=="0-0-0": codigoPais=codigoDep[0]
        for k,v in datos.items():
            codigoDep=k.split("-")
            if "-".join(codigoDep[2:])=="0-0" and codigoPais==codigoDep[0]:
                if "-".join(codigoDep[1:])!="0-0-0":
                    self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 2).addItem(v)
        self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 2).setCurrentIndex(-1)

    def Grabar(self):
        try:
            Estado_Banco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),8).text()
            if Estado_Banco=="BAJA":
                mensajeDialogo("error", "Error", "Banco dado de baja, sin acceso a Grabar")
            else:
                Cod_Prov=self.leCod_Prov.text()
                id=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),0).text()
                p=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 1).currentText()
                for k,v in datos.items():
                    if p==v:
                        Pais=k[0:k.find("-")]
                d=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 2).currentText()
                for k,v in datos.items():
                    if d==v:
                        de=k[k.find("-")+1:]
                        if de[de.find("-")+1:]=="0-0":
                            Departamento=de[0:de.find("-")]

                EntBan=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 3).currentText()
                for k,v in dicbanco.items():
                    if EntBan==v:
                        Entidad_Bancaria=k

                TipCue=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 4).currentText()
                for k,v in TCta.items():
                    if TipCue==k:
                        Tipo_cuenta=v

                Cuenta_Banco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),5).text()

                m=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 6).currentText()
                for k,v in dicmoneda.items():
                    if m==v:
                        Moneda=k

                Cuenta_Interbanco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),7).text()
                Estado_Banco="1"

                Fecha=datetime.now().strftime("%Y-%m-%d")
                Hora=datetime.now().strftime("%H:%M:%S.%f")

                sql ='''INSERT INTO TAB_PROV_007_Bancos_y_cuentas_del_Proveedor(Cod_Prov,Nro_Correlativo,Pais,Departamento,Entidad_Bancaria,Cuenta_Banco,Moneda,Cuenta_Interbanco,Tipo_cuenta,Estado_Banco,Usuario_Reg,Fecha_Reg,Hora_Reg)
                VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (Cod_Prov,id,Pais,Departamento,Entidad_Bancaria,Cuenta_Banco,Moneda,Cuenta_Interbanco,Tipo_cuenta,Estado_Banco,Cod_Usuario,Fecha,Hora)
                respuesta=ejecutarSql(sql)
                if respuesta['respuesta']=='correcto':
                    mensajeDialogo("informacion", "Información", "Registro guardado")

                elif respuesta['respuesta']=='incorrecto':
                    self.pbModificar.setEnabled(False)
                    mensajeDialogo("error", "Error", "No se pudo grabar la información")

                actualizarBan(self,self.tbwReg_Bancos_Cuentas_Prov,sqlBanco,datos,TCta,dicbanco,banco,dicmoneda,mon)

        except Exception as e:
            mensajeDialogo("error", "Error", "Ningun Banco seleccionado")
            print(e)

    def Modificar(self):
        try:
            Estado_Banco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),8).text()
            if Estado_Banco=="BAJA":
                mensajeDialogo("error", "Error", "Banco dado de baja, sin acceso a Modificar")
            else:
                Cod_Prov=self.leCod_Prov.text()
                id=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),0).text()
                p=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 1).currentText()
                for k,v in datos.items():
                    if p==v:
                        Pais=k[0:k.find("-")]
                d=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 2).currentText()
                for k,v in datos.items():
                    if d==v:
                        de=k[k.find("-")+1:]
                        if de[de.find("-")+1:]=="0-0":
                            Departamento=de[0:de.find("-")]

                EntBan=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 3).currentText()
                for k,v in dicbanco.items():
                    if EntBan==v:
                        Entidad_Bancaria=k

                TipCue=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 4).currentText()
                for k,v in TCta.items():
                    if TipCue==k:
                        Tipo_cuenta=v

                Cuenta_Banco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),5).text()

                m=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 6).currentText()
                for k,v in dicmoneda.items():
                    if m==v:
                        Moneda=k

                Cuenta_Interbanco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),7).text()

                Fecha=datetime.now().strftime("%Y-%m-%d")
                Hora=datetime.now().strftime("%H:%M:%S.%f")

                lista=consultarSql(sqlCod_Prov)

                if [Cod_Prov,id] in lista:
                    sql ='''UPDATE TAB_PROV_007_Bancos_y_cuentas_del_Proveedor SET Pais='%s',Departamento='%s',Entidad_Bancaria='%s',Cuenta_Banco='%s',Moneda='%s',Cuenta_Interbanco='%s',Tipo_cuenta='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s'and Nro_Correlativo='%s';'''%(Pais,Departamento,Entidad_Bancaria,Cuenta_Banco,Moneda,Cuenta_Interbanco,Tipo_cuenta,Cod_Usuario,Fecha,Hora,Cod_Prov,id)
                    respuesta=ejecutarSql(sql)
                    if respuesta['respuesta']=='correcto':
                        self.pbModificar.setEnabled(False)
                        mensajeDialogo("informacion", "Información", "Datos modificados con éxito")

                    elif respuesta['respuesta']=='incorrecto':
                        mensajeDialogo("error", "Error", "No se pudo modificar, verifique")
                else:
                    mensajeDialogo("informacion", "Información","No se pudo modificar la información")

                actualizarBan(self,self.tbwReg_Bancos_Cuentas_Prov,sqlBanco,datos,TCta,dicbanco,banco,dicmoneda,mon)

        except Exception as e:
            mensajeDialogo("error", "Error", "Ningun Banco seleccionado")
            print(e)

    def Habilitar(self):
        try:
            Estado_Banco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),8).text()
            if Estado_Banco=="BAJA":
                mensajeDialogo("error", "Error", "Sin acceso a modificar")

            else:
                self.pbGrabar.setEnabled(True)
                Pais=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 1).setEnabled(True)
                Departamento=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 2).setEnabled(True)
                EntidadBancaria=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 3).setEnabled(True)
                TipoCuenta=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 4).setEnabled(True)
                moneda=self.tbwReg_Bancos_Cuentas_Prov.cellWidget(self.tbwReg_Bancos_Cuentas_Prov.currentRow(), 6).setEnabled(True)

                flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                item7=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),5)
                item7.setFlags(flags)
                item9=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),7)
                item9.setFlags(flags)

                self.pbModificar.setEnabled(True)

        except Exception as e:
            mensajeDialogo("error", "Error", "Ningun Banco seleccionado")
            print(e)

    def Baja(self):
        try:
            Cod_Prov=self.leCod_Prov.text()
            id=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),0).text()
            Estado_Banco=self.tbwReg_Bancos_Cuentas_Prov.item(self.tbwReg_Bancos_Cuentas_Prov.currentRow(),8).text()

            Fecha=datetime.now().strftime("%Y-%m-%d")
            Hora=datetime.now().strftime("%H:%M:%S.%f")

            lista=consultarSql(sqlCod_Prov)
            if [Cod_Prov,id] in lista:

                if Estado_Banco=="ACTIVO":
                    reply = mensajeDialogo("pregunta", "Pregunta","¿Realmente desea DAR BAJA al Banco?")
                    if reply == 'Yes':

                        Estado_Banco=2

                        sql ='''UPDATE TAB_PROV_007_Bancos_y_cuentas_del_Proveedor SET Estado_Banco='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s'and Nro_Correlativo='%s';'''%(Estado_Banco,Cod_Usuario,Fecha,Hora,Cod_Prov,id)
                        respuesta=ejecutarSql(sql)
                        if respuesta['respuesta']=='correcto':
                            mensajeDialogo("informacion", "Información", "Banco fue dado de BAJA")

                        elif respuesta['respuesta']=='incorrecto':
                            mensajeDialogo("error", "Error", "No se pudo dar de BAJA")

                else:
                    mensajeDialogo("error", "Error", "Banco ya fue dado de BAJA")

                actualizarBan(self,self.tbwReg_Bancos_Cuentas_Prov,sqlBanco,datos,TCta,dicbanco,banco,dicmoneda,mon)

            else:
                mensajeDialogo("error", "Error", "Banco no registrado, verifique")

        except Exception as e:
            mensajeDialogo("error", "Error", "Ningun Banco seleccionado")
            print(e)

    def Salir(self):
        self.close()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    _main=Bancos()
    _main.showMaximized()
    app.exec_()
