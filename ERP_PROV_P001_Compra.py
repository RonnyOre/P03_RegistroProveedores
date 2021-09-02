import sys
from datetime import datetime
from Funciones04 import *
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import urllib.request

sqlCabecera="SELECT Cod_Soc,Cod_Prov FROM TAB_PROV_008_Cabecera_Datos_de_Compra_del_Proveedor"

sqlDetalle="SELECT Cod_Soc,Cod_Prov,Item FROM TAB_PROV_009_Detalle_Datos_de_Compra_del_Proveedor"

sqlCondPago="SELECT `Descrip_cond`,`Cond_pago` FROM `TAB_COM_003_Condiciones de Pago por Clientes`"

sqlMoneda="SELECT Descrip_moneda,Cod_moneda FROM TAB_SOC_008_Monedas"

class Compra(QMainWindow):
    def __init__(self,codsoc,codusuario,Cod_Prov,Razon_Social):
        QMainWindow.__init__(self)
        uic.loadUi("ERP_PPROV_004.ui",self)

        global Cod_Soc,Cod_Usuario,moneda,condPago,TipoVenta,sqlDet

        Cod_Soc=codsoc
        Cod_Usuario=codusuario

        self.leCod_Prov.setText(Cod_Prov)
        self.leRazon_Social.setText(Razon_Social)
        self.leCod_Prov.setReadOnly(True)
        self.leRazon_Social.setReadOnly(True)
        self.pbModificar.setEnabled(False)

        #Diccionario Moneda
        mon=consultarSql(sqlMoneda)
        moneda={}
        for dato in mon:
            moneda[dato[1]]=dato[0]

        #Diccionario CondPago
        CoPago=consultarSql(sqlCondPago)
        condPago={}
        for dato in CoPago:
            condPago[dato[1]]=dato[0]

        #Diccionario TipoVenta
        TipoVenta={'1':'Crédito','2':'Contado'}
        for k,v in TipoVenta.items():
            self.cbTipo_Venta.addItem(v)
            self.cbTipo_Venta.setCurrentIndex(-1)

        self.tbwDatos_Compra_Prov.currentCellChanged.connect(self.AgregarFila)
        self.pbGrabar.clicked.connect(self.Grabar)
        self.pbHabilitar.clicked.connect(self.Habilitar)
        self.pbModificar.clicked.connect(self.Modificar)
        self.pbRetornar.clicked.connect(self.Salir)
        self.cbTipo_Venta.activated.connect(self.tipoVenta)

        cargarLogo(self.lbLogo_Mp,'multiplay')
        cargarLogo(self.lbLogo_Soc, Cod_Soc)
        cargarIcono(self, 'erp')
        cargarIcono(self.pbGrabar, 'grabar')
        cargarIcono(self.pbModificar, 'modificar')
        cargarIcono(self.pbHabilitar, 'habilitar')
        cargarIcono(self.pbRetornar, 'salir')

        insertarDatos(self.cbMoneda,mon)
        self.cbMoneda.setCurrentIndex(-1)
        insertarDatos(self.cbCondicion_Pago,CoPago)
        self.cbCondicion_Pago.setCurrentIndex(-1)

        sqlDet="SELECT Item,Rango_Inicial,Rango_Final,Porcentaje_desc,Cuotas,Plazo_depósito,Días_reclamo_1,Días_reclamo_2,Días_reclamo_3,Porcentaje_interés FROM TAB_PROV_009_Detalle_Datos_de_Compra_del_Proveedor WHERE Cod_Soc='%s'and Cod_Prov='%s'"%(Cod_Soc,Cod_Prov)
        actualizarComp(self.tbwDatos_Compra_Prov,sqlDet)

    def tipoVenta(self):
        self.leMonto_Max_Cred.setEnabled(True)
        self.cbCondicion_Pago.setEnabled(True)
        TipVen=self.cbTipo_Venta.currentText()
        if TipVen=='Contado':
            self.leMonto_Max_Cred.setEnabled(False)

    def AgregarFila(self,fila,columna):
        if fila==self.tbwDatos_Compra_Prov.rowCount()-1:
            rowPosition = self.tbwDatos_Compra_Prov.rowCount()
            self.tbwDatos_Compra_Prov.insertRow(rowPosition)

            id=self.tbwDatos_Compra_Prov.item(self.tbwDatos_Compra_Prov.currentRow(),0).text()
            flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            sigNro=int(id)+1
            Nro=QTableWidgetItem(str(sigNro))
            Nro.setFlags(flags)
            self.tbwDatos_Compra_Prov.setItem(rowPosition,0, Nro)
            self.tbwDatos_Compra_Prov.resizeColumnToContents(0)

    def Grabar(self):
        try:
            Cod_Prov=self.leCod_Prov.text()

            NombreTV=self.cbTipo_Venta.currentText()
            for k,v in TipoVenta.items():
                if NombreTV==v:
                    Tipo_Venta=k

            NombreMoneda=self.cbMoneda.currentText()
            for k,v in moneda.items():
                if NombreMoneda==v:
                    Moneda=k

            Monto_Crédito=self.leMonto_Max_Cred.text()

            NombreCP=self.cbCondicion_Pago.currentText()
            for k,v in condPago.items():
                if NombreCP==v:
                    Condición_Pago=k

            detalle=[]
            NumCol=self.tbwDatos_Compra_Prov.columnCount()
            for col in range(NumCol):
                    item=self.tbwDatos_Compra_Prov.item(self.tbwDatos_Compra_Prov.currentRow(),col).text()
                    detalle.append(item)

            Item=detalle[0]
            Rango_Inicial=detalle[1]
            Rango_Final=detalle[2]
            Porcentaje_desc=detalle[3]
            Cuotas=detalle[4]
            Plazo_depósito=detalle[5]
            Días_reclamo_1=detalle[6]
            Días_reclamo_2=detalle[7]
            Días_reclamo_3=detalle[8]
            Porcentaje_interés=detalle[9]

            Fecha=datetime.now().strftime("%Y-%m-%d")
            Hora=datetime.now().strftime("%H:%M:%S.%f")

            if len(NombreTV) and len(NombreMoneda) and len(Cod_Prov)!=0:
                sqlCabe='''INSERT INTO TAB_PROV_008_Cabecera_Datos_de_Compra_del_Proveedor(Cod_Soc,Cod_Prov,Item,Tipo_Venta,Moneda,Monto_Crédito,Condición_Pago,Usuario_Reg,Fecha_Reg,Hora_Reg)
                VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (Cod_Soc,Cod_Prov,Item,Tipo_Venta,Moneda,Monto_Crédito,Condición_Pago,Cod_Usuario,Fecha,Hora)
                Cabecera=ejecutarSql(sqlCabe)
                sqlDeta='''INSERT INTO TAB_PROV_009_Detalle_Datos_de_Compra_del_Proveedor(Cod_Soc,Cod_Prov,Item,Rango_Inicial,Rango_Final,Porcentaje_desc,Cuotas,Plazo_depósito,Días_reclamo_1,Días_reclamo_2,Días_reclamo_3,Porcentaje_interés,Usuario_Reg,Fecha_Reg,Hora_Reg)
                VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (Cod_Soc,Cod_Prov,Item,Rango_Inicial,Rango_Final,Porcentaje_desc,Cuotas,Plazo_depósito,Días_reclamo_1,Días_reclamo_2,Días_reclamo_3,Porcentaje_interés,Cod_Usuario,Fecha,Hora)
                respuesta=ejecutarSql(sqlDeta)
                if respuesta['respuesta']=='correcto':
                    mensajeDialogo("informacion", "Información", "Registro guardado")
                    self.cbTipo_Venta.setCurrentIndex(-1)
                    self.cbMoneda.setCurrentIndex(-1)
                    self.leMonto_Max_Cred.clear()
                    self.cbCondicion_Pago.setCurrentIndex(-1)

                elif respuesta['respuesta']=='incorrecto':
                    self.pbModificar.setEnabled(False)
                    mensajeDialogo("error", "Error", "Ingrese Datos Válido")
            else:
                mensajeDialogo("error", "Error", "Llene todos los campos obligatorios")

            actualizarComp(self.tbwDatos_Compra_Prov,sqlDet)

        except Exception as e:
            mensajeDialogo("error", "Error", "Llene todos los campos")
            print(e)

    def Modificar(self):
        try:
            Cod_Prov=self.leCod_Prov.text()

            NombreTV=self.cbTipo_Venta.currentText()
            for k,v in TipoVenta.items():
                if NombreTV==v:
                    Tipo_Venta=k

            NombreMoneda=self.cbMoneda.currentText()
            for k,v in moneda.items():
                if NombreMoneda==v:
                    Moneda=k

            Monto_Crédito=self.leMonto_Max_Cred.text()

            NombreCP=self.cbCondicion_Pago.currentText()
            for k,v in condPago.items():
                if NombreCP==v:
                    Condición_Pago=k

            detalle=[]
            NumCol=self.tbwDatos_Compra_Prov.columnCount()
            for col in range(NumCol):
                    item=self.tbwDatos_Compra_Prov.item(self.tbwDatos_Compra_Prov.currentRow(),col).text()
                    detalle.append(item)

            Item=detalle[0]
            Rango_Inicial=detalle[1]
            Rango_Final=detalle[2]
            Porcentaje_desc=detalle[3]
            Cuotas=detalle[4]
            Plazo_depósito=detalle[5]
            Días_reclamo_1=detalle[6]
            Días_reclamo_2=detalle[7]
            Días_reclamo_3=detalle[8]
            Porcentaje_interés=detalle[9]

            Fecha=datetime.now().strftime("%Y-%m-%d")
            Hora=datetime.now().strftime("%H:%M:%S.%f")

            listaDeta=consultarSql(sqlDetalle)

            if [Cod_Soc,Cod_Prov,Item] in listaDeta:
                sqlDeta ='''UPDATE TAB_PROV_009_Detalle_Datos_de_Compra_del_Proveedor SET Rango_Inicial='%s',Rango_Final='%s',Porcentaje_desc='%s',Cuotas='%s',Plazo_depósito='%s',Días_reclamo_1='%s',Días_reclamo_2='%s',Días_reclamo_3='%s',Porcentaje_interés='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s'
                WHERE Cod_Soc='%s' and Cod_Prov='%s' and Item='%s';''' %(Rango_Inicial,Rango_Final,Porcentaje_desc,Cuotas,Plazo_depósito,Días_reclamo_1,Días_reclamo_2,Días_reclamo_3,Porcentaje_interés,Cod_Usuario,Fecha,Hora,Cod_Soc,Cod_Prov,Item)

                sqlCabe ='''UPDATE TAB_PROV_008_Cabecera_Datos_de_Compra_del_Proveedor SET Tipo_Venta='%s',Moneda='%s',Monto_Crédito='%s',Condición_Pago='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s'
                WHERE Cod_Soc='%s' and Cod_Prov='%s'and Item='%s';''' %(Tipo_Venta,Moneda,Monto_Crédito,Condición_Pago,Cod_Usuario,Fecha,Hora,Cod_Soc,Cod_Prov,Item)
                resp=ejecutarSql(sqlCabe)
                respuesta=ejecutarSql(sqlDeta)
                if respuesta['respuesta']=='correcto':
                    self.pbModificar.setEnabled(False)
                    mensajeDialogo("informacion", "Información", "Datos modificados con éxito")
                    self.cbTipo_Venta.setCurrentIndex(-1)
                    self.cbMoneda.setCurrentIndex(-1)
                    self.leMonto_Max_Cred.clear()
                    self.cbCondicion_Pago.setCurrentIndex(-1)

                elif respuesta['respuesta']=='incorrecto':
                    mensajeDialogo("error", "Error", "No se pudo modificar, verifique")

            else:
                mensajeDialogo("informacion", "Información","No se pudo modificar la información")

            actualizarComp(self.tbwDatos_Compra_Prov,sqlDet)

        except Exception as e:
            mensajeDialogo("error", "Error", "Llene todos los campos")
            print(e)

    def Habilitar(self):
        try:
            NumCol=self.tbwDatos_Compra_Prov.columnCount()
            flags = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            for col in range(NumCol):
                if col!=0:
                    dat=self.tbwDatos_Compra_Prov.item(self.tbwDatos_Compra_Prov.currentRow(),col)
                    dat.setFlags(flags)

            Cod_Prov=self.leCod_Prov.text()
            Item=self.tbwDatos_Compra_Prov.item(self.tbwDatos_Compra_Prov.currentRow(),0).text()
            sqlCab="SELECT Tipo_Venta,Moneda,Monto_Crédito,Condición_Pago FROM TAB_PROV_008_Cabecera_Datos_de_Compra_del_Proveedor WHERE Cod_Soc='%s' and Cod_Prov='%s'and Item='%s'"%(Cod_Soc,Cod_Prov,Item)
            cab=convlist(sqlCab)

            self.cbTipo_Venta.setCurrentIndex(int(cab[0])-1)
            self.cbMoneda.setCurrentIndex(int(cab[1])-1)
            if cab[2]=='0.00':
                monto=''
                self.leMonto_Max_Cred.setText(monto)
            else:
                self.leMonto_Max_Cred.setText(cab[2])

            self.cbCondicion_Pago.setCurrentIndex(int(cab[3])-1)
            self.pbModificar.setEnabled(True)

        except Exception as e:
            mensajeDialogo("error", "Error", "Llene todos los campos")
            print(e)

    def Salir(self):
        self.close()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    _main=Compra()
    _main.showMaximized()
    app.exec_()
