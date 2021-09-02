import sys
from datetime import datetime
from Funciones04 import *
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import urllib.request

sqlCod_Prov= "SELECT Cod_Prov,Tipo_Inter_Prov FROM TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor"

sqlTipo_Inter="SELECT Descrip_inter,Cod_tipo_inter FROM TAB_SOC_014_Tipo_de_Interlocutor"

sqlDNI_Inter="SELECT DNI_Inter FROM TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor"

class Interlocutores(QMainWindow):
    def __init__(self,codsoc,codusuario,Cod_Prov,Razon_Social):
        QMainWindow.__init__(self)
        uic.loadUi("ERP_PPROV_002.ui",self)

        global Cod_Soc,Cod_Usuario,dicTipoInter,sqlInter,Tipo_Inter

        Cod_Soc=codsoc
        Cod_Usuario=codusuario

        self.leCod_Prov.setText(Cod_Prov)
        self.leRazon_Social.setText(Razon_Social)
        self.leCod_Prov.setReadOnly(True)
        self.leRazon_Social.setReadOnly(True)
        self.pbModificar.setEnabled(False)

        self.pbGrabar.clicked.connect(self.Grabar)
        self.pbHabilitar.clicked.connect(self.Habilitar)
        self.pbModificar.clicked.connect(self.Modificar)
        self.pbRetornar.clicked.connect(self.Retornar)
        self.pbBaja.clicked.connect(self.Baja)
        self.tbwRegistro_Prov.currentCellChanged.connect(self.AgregarFila)

        cargarLogo(self.lbLogo_Mp,'multiplay')
        cargarLogo(self.lbLogo_Soc, Cod_Soc)
        cargarIcono(self, 'erp')
        cargarIcono(self.pbGrabar, 'grabar')
        cargarIcono(self.pbModificar, 'modificar')
        cargarIcono(self.pbHabilitar, 'habilitar')
        cargarIcono(self.pbBaja, 'darbaja')
        cargarIcono(self.pbRetornar, 'salir')

        Tipo_Inter = consultarSql(sqlTipo_Inter)
        dicTipoInter={}
        for dato in Tipo_Inter:
            dicTipoInter[dato[1]]=dato[0]

        sqlInter="SELECT Tipo_Inter_Prov,Nombre_Inter,Correo_Inter,DNI_Inter,Anexo,Telef_Fijo,Telef_Inter,Estado_Inter FROM TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor WHERE Cod_Prov='%s'" %(Cod_Prov)
        actualizarInter(self,self.tbwRegistro_Prov,sqlInter,Tipo_Inter,dicTipoInter)

    def AgregarFila(self,fila,columna):
        if fila==self.tbwRegistro_Prov.rowCount()-1:
            rowPosition = self.tbwRegistro_Prov.rowCount()
            self.tbwRegistro_Prov.insertRow(rowPosition)

            flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item=QTableWidgetItem()
            item.setFlags(flags)
            self.tbwRegistro_Prov.setItem(rowPosition,7, item)

            cb = QComboBox(self.tbwRegistro_Prov)
            self.tbwRegistro_Prov.setCellWidget(rowPosition, 0, cb)
            insertarDatos(cb,Tipo_Inter)
            cb.setCurrentIndex(-1)
            font = QtGui.QFont()
            font.setPointSize(12)
            cb.setFont(font)
            self.tbwRegistro_Prov.resizeColumnToContents(0)

    def Grabar(self):
        try:
            Estado=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),7).text()
            if Estado=="BAJA":
                mensajeDialogo("error", "Error", "Sin acceso a Grabar")
            else:
                TIP=verificarTIP(self.tbwRegistro_Prov)
                Descrip_inter=self.tbwRegistro_Prov.cellWidget(self.tbwRegistro_Prov.currentRow(), 0).currentText()
                for k,v in dicTipoInter.items():
                    if Descrip_inter==v:
                        Tipo_Inter_Prov=k

                if Descrip_inter in TIP:
                    mensajeDialogo("error", "Error", "Tipo de Interlocutor ya existe")
                    self.tbwRegistro_Prov.cellWidget(self.tbwRegistro_Prov.currentRow(), 0).setCurrentIndex(-1)

                else:
                    Cod_Prov=self.leCod_Prov.text()
                    data=[]
                    d=self.tbwRegistro_Prov.columnCount()-1
                    for n in range(d):
                        if n!=0:
                            m=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),n).text()
                            data.append(m)

                    Nombre_Inter=data[0]
                    Correo_Inter=data[1]
                    DNI_Inter=data[2]
                    Anexo=data[3]
                    Telf_Fijo=data[4]
                    Telf_Inter=data[5]
                    Estado_Inter=1

                    Fecha=datetime.now().strftime("%Y-%m-%d")
                    Hora=datetime.now().strftime("%H:%M:%S.%f")

                    sql ='''INSERT INTO TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor (Cod_Prov,Tipo_Inter_Prov,Nombre_Inter,Correo_Inter,DNI_Inter,Anexo,Telef_Fijo,Telef_Inter,Estado_Inter,Usuario_Reg,Fecha_Reg,Hora_Reg)
                    VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (Cod_Prov,Tipo_Inter_Prov,Nombre_Inter,Correo_Inter,DNI_Inter,Anexo,Telf_Fijo,Telf_Inter,Estado_Inter,Cod_Usuario,Fecha,Hora)
                    respuesta=ejecutarSql(sql)
                    if respuesta['respuesta']=='correcto':
                        mensajeDialogo("informacion", "Información","Registro guardado")

                    elif respuesta['respuesta']=='incorrecto':
                        self.pbModificar.setEnabled(False)
                        mensajeDialogo("error", "Error", "No se pudo grabar la información")

                    actualizarInter(self,self.tbwRegistro_Prov,sqlInter,Tipo_Inter,dicTipoInter)

        except Exception as e:
            mensajeDialogo("error", "Error", "Faltan datos, verifique")
            print(e)

    def Modificar(self):
        try:
            Estado=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),7).text()
            if Estado=="BAJA":
                mensajeDialogo("error", "Error", "Interlocutor dado de baja, sin acceso a Modificar")
            else:
                TIP=verificarTIP(self.tbwRegistro_Prov)
                Descrip_inter=self.tbwRegistro_Prov.cellWidget(self.tbwRegistro_Prov.currentRow(), 0).currentText()
                for k,v in dicTipoInter.items():
                    if Descrip_inter==v:
                        Tipo_Inter_Prov=k

                if Descrip_inter in TIP:
                    mensajeDialogo("error", "Error", "Tipo de Interlocutor ya existe")
                    self.tbwRegistro_Prov.cellWidget(self.tbwRegistro_Prov.currentRow(), 0).setCurrentIndex(-1)

                else:
                    Cod_Prov=self.leCod_Prov.text()
                    data=[]
                    d=self.tbwRegistro_Prov.columnCount()-1
                    for n in range(d):
                        if n!=0:
                            m=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),n).text()
                            data.append(m)

                    Nombre_Inter=data[0]
                    Correo_Inter=data[1]
                    DNI_Inter=data[2]
                    Anexo=data[3]
                    Telf_Fijo=data[4]
                    Telf_Inter=data[5]
                    Estado_Inter=1

                    Fecha=datetime.now().strftime("%Y-%m-%d")
                    Hora=datetime.now().strftime("%H:%M:%S.%f")

                    lista = consultarSql(sqlCod_Prov)

                    if [Cod_Prov,Tipo_Inter_Prov] in lista:
                        sql ='''UPDATE TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor SET Nombre_Inter='%s',Correo_Inter='%s',DNI_Inter='%s',Anexo='%s',Telef_Fijo='%s',Telef_Inter='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s'and Tipo_Inter_Prov='%s';'''%(Nombre_Inter,Correo_Inter,DNI_Inter,Anexo,Telf_Fijo,Telf_Inter,Cod_Usuario,Fecha,Hora,Cod_Prov,Tipo_Inter_Prov)
                        respuesta=ejecutarSql(sql)
                        if respuesta['respuesta']=='correcto':
                            self.pbModificar.setEnabled(False)
                            mensajeDialogo("informacion", "Información","Datos modificados con éxito")

                        elif respuesta['respuesta']=='incorrecto':
                            mensajeDialogo("error", "Error", "No se pudo modificar, verifique")
                    else:
                        mensajeDialogo("informacion", "Información","No se pudo modificar la información")

                    actualizarInter(self,self.tbwRegistro_Prov,sqlInter,Tipo_Inter,dicTipoInter)

        except Exception as e:
            mensajeDialogo("error", "Error", "Faltan datos, verifique")
            print(e)

    def Habilitar(self):
        try:
            Estado_Inter=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),7).text()
            if Estado_Inter=="BAJA":
                mensajeDialogo("error", "Error", "Sin acceso a modificar")

            else:
                self.pbGrabar.setEnabled(True)
                DNI_Inter=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),3).text()
                sql1= "SELECT Cod_Prov FROM TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor WHERE DNI_Inter='%s'" %(DNI_Inter)
                lista=convlist(sql1)
                self.leCod_Prov.setText(lista[0])
                sql2= "SELECT Razón_Social FROM TAB_PROV_001_Registro_de_Proveedores WHERE Cod_Prov='%s'" %(lista[0])
                data=convlist(sql2)
                self.leRazon_Social.setText(data[0])
                NumCol=self.tbwRegistro_Prov.columnCount()
                flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                for col in range(NumCol):
                    if col!=0 and col != 7:
                        item=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),col)
                        item.setFlags(flags)

                self.pbModificar.setEnabled(True)

        except Exception as e:
            mensajeDialogo("error", "Error", "Interlocutor no seleccionado, verifique")
            print(e)

    def Baja(self):
        try:
            Cod_Prov=self.leCod_Prov.text()
            Descrip_inter=self.tbwRegistro_Prov.cellWidget(self.tbwRegistro_Prov.currentRow(), 0).currentText()
            for k,v in dicTipoInter.items():
                if Descrip_inter==v:
                    Tipo_Inter_Prov=k

            Estado_Inter=self.tbwRegistro_Prov.item(self.tbwRegistro_Prov.currentRow(),7).text()

            Fecha=datetime.now().strftime("%Y-%m-%d")
            Hora=datetime.now().strftime("%H:%M:%S.%f")

            lista = consultarSql(sqlCod_Prov)

            if [Cod_Prov,Tipo_Inter_Prov] in lista:
                if Estado_Inter=="ACTIVO":
                    reply = mensajeDialogo("pregunta", "Pregunta","¿Realmente desea DAR BAJA al Interlocutor?")
                    if reply == 'Yes':

                        Estado_Inter=2

                        sql ='''UPDATE TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor SET Estado_Inter='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s'and Tipo_Inter_Prov='%s';'''%(Estado_Inter,Cod_Usuario,Fecha,Hora,Cod_Prov,Tipo_Inter_Prov)
                        respuesta=ejecutarSql(sql)
                        if respuesta['respuesta']=='correcto':
                            mensajeDialogo("informacion", "Información", "Interlocutor fue dado de BAJA")

                        elif respuesta['respuesta']=='incorrecto':
                            mensajeDialogo("error", "Error", "No se pudo dar de BAJA")

                else:
                    mensajeDialogo("error", "Error", "Interlocutor ya fue dado de BAJA")

                actualizarInter(self,self.tbwRegistro_Prov,sqlInter,Tipo_Inter,dicTipoInter)
            else:
                mensajeDialogo("error", "Error", "Aún no se ha registrado Interlocutor")

        except Exception as e:
            mensajeDialogo("error", "Error", "Ningun Interlocutor seleccionado")
            print(e)



    def Retornar(self):
        self.close()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    _main=Interlocutores()
    _main.showMaximized()
    app.exec_()
