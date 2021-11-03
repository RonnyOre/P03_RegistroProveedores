import sys
from datetime import datetime
from Funciones04 import *
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import urllib.request
from ERP_PROV_P001_Interlocutores import Interlocutores
from ERP_PROV_P001_Bancos import Bancos
from ERP_PROV_P001_Compra import Compra

TipProv={'1':'Materiales','2':'Servicios','3':'Materiales y Servicios','4':'Transportes','5':'Agente Aduanas'}

class Buscar(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("ERP_PROV_P001_Buscar.ui",self)

        self.twProveedores.itemDoubleClicked.connect(self.Proveedor)
        self.lePalabra.textChanged.connect(self.buscar)

        cargarIcono(self, 'erp')

        sqlProv="SELECT Cod_prov,Tip_prov,Razón_social, RUC_NIF, Estado_Prov FROM TAB_PROV_001_Registro_de_Proveedores"
        Prov=consultarSql(sqlProv)

        self.twProveedores.clear()
        for fila in Prov:
            if fila[1] in TipProv:
                fila[1]=TipProv[fila[1]]
            if fila[4]=='1':
                fila[4]='ACTIVO'
            else:
                fila[4]='BAJA'
            item=QTreeWidgetItem(self.twProveedores,fila)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setTextAlignment(0,QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item.setTextAlignment(3,QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item.setTextAlignment(4,QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.twProveedores.addTopLevelItem(item)
        self.twProveedores.resizeColumnToContents(0)
        self.twProveedores.resizeColumnToContents(1)
        self.twProveedores.resizeColumnToContents(2)
        self.twProveedores.resizeColumnToContents(3)

    def buscar(self):
        buscarTabla(self.twProveedores, self.lePalabra.text(), [1,2,3])

    def Proveedor(self,item):
        global Codigo_Proveedor
        Codigo_Proveedor=item.text(0)
        self.close()

class ERP_PPROV_001(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("ERP_PPROV_001.ui",self)

        global Cod_Soc,Nom_Soc,Cod_Usuario

        Cod_Soc='1000'
        Nom_Soc='MULTICABLE PERU SOCIEDAD ANONIMA CERRADA'
        Cod_Usuario='2021100004'

        self.leTelf_Fijo.setValidator(QIntValidator())
        self.leAnexo.setValidator(QIntValidator())
        self.leFax.setValidator(QIntValidator())
        self.leTelf_Cel.setValidator(QIntValidator())
        # self.leDNI.setValidator(QIntValidator())
        self.leTelf_Cel_Repre.setValidator(QIntValidator())

        self.leerDatos()
        self.cargarPais()
        self.cargarTipoProv()
        self.cargarCodProv()
        self.pbInterlocutores.clicked.connect(self.Inter)
        self.pbBancos.clicked.connect(self.Ban)
        self.pbDatos_Compra.clicked.connect(self.Comp)
        self.pbGrabar.clicked.connect(self.Grabar)
        self.pbHabilitar.clicked.connect(self.Habilitar)
        self.pbModificar.clicked.connect(self.Modificar)
        self.pbBaja.clicked.connect(self.DardeBaja)
        self.pbSalir.clicked.connect(self.Salir)
        self.pbSeleccionar.clicked.connect(self.Seleccionar)
        self.pbNuevo.clicked.connect(self.Nuevo)

        self.cbPais.activated.connect(self.cargarDepartamento)
        self.cbDep.activated.connect(self.cargarProvincia)
        self.cbProvincia.activated.connect(self.cargarDistrito)
        self.cbDistrito.activated.connect(self.ubigeo)
        self.leRUC.returnPressed.connect(self.consultaRUC)

        self.leCorreo_Emp.editingFinished.connect(self.validarCorreo)
        self.leCorreo_Repre.editingFinished.connect(self.validarCorreo)
        self.leDNI.editingFinished.connect(self.validarNumero)
        self.leCod_Prov.returnPressed.connect(self.consultaProv)

        self.pbInterlocutores.setEnabled(False)
        self.pbBancos.setEnabled(False)
        self.pbDatos_Compra.setEnabled(False)
        self.pbHabilitar.setEnabled(False)

    # def datosGenerales(self, codSoc, empresa, usuario):
    #     global Cod_Soc, Nom_Soc, Cod_Usuario
    #     Cod_Soc = codSoc
    #     Nom_Soc = empresa
    #     Cod_Usuario = usuario

        cargarLogo(self.lbLogo_Mp,'multiplay')
        cargarLogo(self.lbLogo_Soc, Cod_Soc)
        cargarIcono(self, 'erp')
        cargarIcono(self.pbInterlocutores, 'usuario')
        cargarIcono(self.pbBancos, 'banco')
        cargarIcono(self.pbDatos_Compra, 'compra')
        cargarIcono(self.pbGrabar, 'grabar')
        cargarIcono(self.pbModificar, 'modificar')
        cargarIcono(self.pbHabilitar, 'habilitar')
        cargarIcono(self.pbBaja, 'darbaja')
        cargarIcono(self.pbSalir, 'salir')
        cargarIcono(self.pbSeleccionar, 'buscar')
        cargarIcono(self.pbNuevo, 'nuevo')

    def cargarCodProv(self):
        self.pbModificar.setEnabled(False)
        self.pbBaja.setEnabled(False)
        # self.leCod_Prov.setReadOnly(True)
        self.leRazon_Social.setReadOnly(True)
        self.leDirecc_Prov.setReadOnly(True)
        self.leActivo_Baja.setReadOnly(True)
        self.leEstado_Prov.setReadOnly(True)
        self.leUbigeo.setReadOnly(True)

    def cargarTipoProv(self):
        for k,v in TipProv.items():
            self.cbTipo_Prov.addItem(v)
            self.cbTipo_Prov.setCurrentIndex(-1)

    def consultaProv(self):
        global Codigo_Proveedor
        Codigo_Proveedor=self.leCod_Prov.text()
        if len(Codigo_Proveedor)!=0:
            self.Cargar_Proveedor()
            self.leCod_Prov.setReadOnly(True)

    def Nuevo(self):
        global Codigo_Proveedor
        Codigo_Proveedor=None

        self.leCod_Prov.clear()
        self.cbTipo_Prov.setCurrentIndex(-1)
        self.leRUC.clear()
        self.leEstado_Prov.clear()
        self.leActivo_Baja.clear()
        self.leDirecc_Prov.clear()
        self.leRazon_Social.clear()
        self.cbPais.setCurrentIndex(-1)
        self.cbDep.setCurrentIndex(-1)
        self.cbProvincia.setCurrentIndex(-1)
        self.cbDistrito.setCurrentIndex(-1)
        self.leUbigeo.clear()
        self.leTelf_Fijo.clear()
        self.leAnexo.clear()
        self.leFax.clear()
        self.leTelf_Cel.clear()
        self.leCorreo_Emp.clear()
        self.leRepre_Emp.clear()
        self.leDNI.clear()
        self.leCorreo_Repre.clear()
        self.leTelf_Cel_Repre.clear()

        self.pbModificar.setEnabled(False)
        self.pbBaja.setEnabled(False)
        self.pbGrabar.setEnabled(True)
        self.leCod_Prov.setReadOnly(False)
        self.cbTipo_Prov.setEnabled(True)
        self.leRUC.setReadOnly(False)
        self.cbPais.setEnabled(True)
        self.cbDep.setEnabled(False)
        self.cbProvincia.setEnabled(False)
        self.cbDistrito.setEnabled(False)
        self.leTelf_Fijo.setReadOnly(False)
        self.leAnexo.setReadOnly(False)
        self.leFax.setReadOnly(False)
        self.leTelf_Cel.setReadOnly(False)
        self.leRepre_Emp.setReadOnly(False)
        self.leCorreo_Emp.setReadOnly(False)
        self.leDNI.setReadOnly(False)
        self.leCorreo_Repre.setReadOnly(False)
        self.leTelf_Cel_Repre.setReadOnly(False)

        self.pbInterlocutores.setEnabled(False)
        self.pbBancos.setEnabled(False)
        self.pbDatos_Compra.setEnabled(False)

    def Seleccionar(self):
        global Codigo_Proveedor
        Codigo_Proveedor=None

        Buscar().exec_()
        self.Cargar_Proveedor()

    def Cargar_Proveedor(self):
        try:
            # sqlCodProv="SELECT Razón_social,Tip_Prov,Nro_Telf,Correo,Direcc_prov,País,Departamento,Provincia,Distrito,Nro_Telf_Emp,Nro_Fax,Anexo,RUC_NIF,Representante,DNI_Repre,Correo_Repre,Telf_Repre,Estado_Prov FROM TAB_PROV_001_Registro_de_Proveedores WHERE Cod_prov='%s';"%(Codigo_Proveedor)
            sqlCodProv='''SELECT a.Razón_social,a.Tip_Prov,a.Nro_Telf,a.Correo,a.Direcc_prov,CONCAT(a.País,' - ',b.Nombre),CONCAT(a.Departamento,' - ',c.Nombre),CONCAT(a.Provincia,' - ',d.Nombre),CONCAT(a.Distrito,' - ', e.Nombre),a.Ubigeo,a.Nro_Telf_Emp,a.Nro_Fax,a.Anexo,a.RUC_NIF,a.Representante,a.DNI_Repre,a.Correo_Repre,a.Telf_Repre,a.Estado_Prov
            FROM TAB_PROV_001_Registro_de_Proveedores a
            LEFT JOIN TAB_SOC_009_Ubigeo_NuevaVersion b ON b.Cod_Pais=a.País AND b.Cod_Depart_Region='00' AND b.Cod_Provincia='00' AND b.Cod_Distrito='00'
            LEFT JOIN TAB_SOC_009_Ubigeo_NuevaVersion c ON c.Cod_Pais=a.País AND c.Cod_Depart_Region=a.Departamento AND c.Cod_Provincia='00' AND c.Cod_Distrito='00'
            LEFT JOIN TAB_SOC_009_Ubigeo_NuevaVersion d ON d.Cod_Pais=a.País AND d.Cod_Depart_Region=a.Departamento AND d.Cod_Provincia=a.Provincia AND d.Cod_Distrito='00'
            LEFT JOIN TAB_SOC_009_Ubigeo_NuevaVersion e ON e.Cod_Pais=a.País AND e.Cod_Depart_Region=a.Departamento AND e.Cod_Provincia=a.Provincia AND e.Cod_Distrito=a.Distrito
            WHERE a.Cod_prov='%s';'''%(Codigo_Proveedor)

            lista=convlist(sqlCodProv)
            print(lista)
            for i in range(len(lista)):
                if lista[i]=='0':
                    lista[i]=""

            self.pbGrabar.setEnabled(False)
            self.cbTipo_Prov.setCurrentIndex(int(lista[1])-1)
            self.leRUC.setText(lista[13])
            self.leEstado_Prov.setText(lista[18])

            if lista[18]=="1":
                self.leActivo_Baja.setText("ACTIVO")
                self.leActivo_Baja.setStyleSheet("")
                self.leActivo_Baja.setStyleSheet("background-color: rgb(255,255,255);")
                self.pbHabilitar.setEnabled(True)
                self.pbBaja.setEnabled(True)

            elif lista[18]=="2":
                self.leActivo_Baja.setText("BAJA")
                self.leActivo_Baja.setStyleSheet("color: rgb(255,0,0);\n""background-color: rgb(255,255,255);")
                self.pbHabilitar.setEnabled(False)
                self.pbModificar.setEnabled(False)
                self.pbBaja.setEnabled(False)

            self.leCod_Prov.setText(Codigo_Proveedor)
            self.leCod_Prov.setReadOnly(True)
            self.leDirecc_Prov.setText(lista[4])
            self.leRazon_Social.setText(lista[0])

            self.cbPais.setCurrentIndex(self.cbPais.findText(lista[5]))
            self.cbPais.setEnabled(False)
            self.cargarDepartamento()
            self.cbDep.setCurrentIndex(self.cbDep.findText(lista[6]))
            self.cargarProvincia()
            self.cbProvincia.setCurrentIndex(self.cbProvincia.findText(lista[7]))
            self.cargarDistrito()
            self.cbDistrito.setCurrentIndex(self.cbDistrito.findText(lista[8]))

            cbPais=self.cbPais.currentText()
            Pais=cbPais[0:cbPais.find("-")-1]
            if Pais=='01':
                self.leUbigeo.setText(lista[9])
            else:
                self.leUbigeo.setText("")

            self.leTelf_Fijo.setText(lista[2])
            self.leAnexo.setText(lista[12])
            self.leFax.setText(lista[11])
            self.leTelf_Cel.setText(lista[10])
            self.leCorreo_Emp.setText(lista[3])
            self.leRepre_Emp.setText(lista[14])
            self.leDNI.setText(lista[15])
            self.leCorreo_Repre.setText(lista[16])
            self.leTelf_Cel_Repre.setText(lista[17])

            self.cbTipo_Prov.setEnabled(False)
            self.cbTipo_Prov.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
            self.leRUC.setReadOnly(True)
            self.leEstado_Prov.setReadOnly(True)
            self.cbPais.setEnabled(False)
            self.cbPais.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
            self.cbDep.setEnabled(False)
            self.cbDep.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
            self.cbProvincia.setEnabled(False)
            self.cbProvincia.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
            self.cbDistrito.setEnabled(False)
            self.cbDistrito.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
            self.leUbigeo.setReadOnly(True)
            self.leTelf_Fijo.setReadOnly(True)
            self.leAnexo.setReadOnly(True)
            self.leFax.setReadOnly(True)
            self.leTelf_Cel.setReadOnly(True)
            self.leRepre_Emp.setReadOnly(True)
            self.leCorreo_Emp.setReadOnly(True)
            self.leDNI.setReadOnly(True)
            self.leCorreo_Repre.setReadOnly(True)
            self.leTelf_Cel_Repre.setReadOnly(True)

            self.pbInterlocutores.setEnabled(True)
            self.pbBancos.setEnabled(True)
            self.pbDatos_Compra.setEnabled(True)

        except Exception as e:
            if len(self.leCod_Prov.text())==0:
                self.leCod_Prov.setReadOnly(False)
                self.pbGrabar.setEnabled(True)
                self.cbDep.setEnabled(False)
                self.cbProvincia.setEnabled(False)
                self.cbDistrito.setEnabled(False)
                self.pbInterlocutores.setEnabled(False)
                self.pbBancos.setEnabled(False)
                self.pbDatos_Compra.setEnabled(False)
            print(e)

    def consultaRUC(self):
        try:
            if len(self.leRUC.text())!=11:
                mensajeDialogo("informacion", "Información", "Número RUC no valido")
                self.leRUC.clear()
            else:
                RUC=self.leRUC.text()
                sqlRUC="SELECT RUC_NIF FROM TAB_PROV_001_Registro_de_Proveedores"
                lista=convlist(sqlRUC)
                if RUC in lista:
                    mensajeDialogo("error", "Error", "RUC de Proveedor ya existe")
                    self.leRUC.clear()
                else:
                    data=consultaRuc(True, RUC)
                    if data!=[]:
                        self.leRazon_Social.setText(data[1])
                        self.leDirecc_Prov.setText(data[3])
                        if data[4]=="ACTIVO":
                            self.leActivo_Baja.setText(data[4])
                            self.leActivo_Baja.setStyleSheet("background-color: rgb(255,255,255);")
                            self.leEstado_Prov.setText("1")
                            self.pbGrabar.setEnabled(True)
                            self.leRUC.setReadOnly(True)
                        else:
                            self.leActivo_Baja.setText(data[4])
                            self.leActivo_Baja.setStyleSheet("color: rgb(255,0,0);\n""background-color: rgb(255,255,255);")
                            self.leEstado_Prov.setText("2")
                            self.pbGrabar.setEnabled(False)
                            self.leRUC.setReadOnly(False)
                            mensajeDialogo("informacion", "Información", "Número RUC en estado de Baja")

        except Exception as e:
            # mensajeDialogo("informacion", "Información", "No se encontró RUC o No está conectado")
            self.leRUC.clear()
            print(e)

    def leerDatos(self):
        global datos
        sql="SELECT * FROM `TAB_SOC_009_Ubigeo_NuevaVersion` ORDER BY Cod_Distrito ASC, Cod_Provincia ASC, Cod_Depart_Region ASC, Cod_Pais ASC"
        respuesta=consultarSql(sql)
        datos={}
        for dato in respuesta:
            codigo="-".join(dato[0:4])
            if codigo not in datos: datos[codigo]=dato[4]

    def cargarPais(self):
        for k,v in datos.items():
            codigo=k.split("-")
            if "-".join(codigo[1:])=="00-00-00": self.cbPais.addItem(codigo[0]+" - "+v)
        self.cbPais.setCurrentIndex(-1)
        self.cbDep.setEnabled(False)
        self.cbProvincia.setEnabled(False)
        self.cbDistrito.setEnabled(False)

    def cargarDepartamento(self):
        self.cbDep.setEnabled(False)
        self.cbProvincia.setEnabled(False)
        self.cbDistrito.setEnabled(False)

        texto=self.cbPais.currentText()
        pais=texto[texto.find("-")+2:]

        if pais=="": return
        self.cbDep.clear()
        for k,v in datos.items():
            codigoDep=k.split("-")
            if v==pais and "-".join(codigoDep[1:])=="00-00-00": codigoPais=codigoDep[0]
        for k,v in datos.items():
            codigoDep=k.split("-")
            if "-".join(codigoDep[2:])=="00-00" and codigoPais==codigoDep[0]:
                if "-".join(codigoDep[1:])!="00-00-00": self.cbDep.addItem(codigoDep[1]+" - "+v)
        self.cbDep.setCurrentIndex(-1)
        self.cbProvincia.clear()
        self.cbProvincia.clearEditText()
        self.cbDistrito.clear()
        self.cbDistrito.clearEditText()
        self.leUbigeo.clear()
        self.cbDep.setEnabled(True)

    def cargarProvincia(self):
        self.cbProvincia.setEnabled(False)
        self.cbDistrito.setEnabled(False)

        texto=self.cbDep.currentText()
        departamento=texto[texto.find("-")+2:]

        if departamento=="": return
        cbPais=self.cbPais.currentText()
        pais=cbPais[cbPais.find("-")+2:]
        self.cbProvincia.clear()
        codigoPais=""
        for k,v in datos.items():
            codigoProv=k.split("-")
            if v==pais and "-".join(codigoProv[1:])=="00-00-00": codigoPais=codigoProv[0]
            if v==departamento and "-".join(codigoProv[2:])=="00-00" and codigoPais==codigoProv[0]: codigoDep=codigoProv[0:2]
        for k,v in datos.items():
            codigoProv=k.split("-")
            if codigoProv[3]=="00" and codigoDep==codigoProv[0:2] and codigoPais==codigoProv[0]:
                if "-".join(codigoProv[2:])!="00-00": self.cbProvincia.addItem(codigoProv[2]+" - "+v)
        self.cbProvincia.setCurrentIndex(-1)
        self.cbDistrito.clear()
        self.cbDistrito.clearEditText()
        self.leUbigeo.clear()

        if pais =="PERU": self.cbProvincia.setEnabled(True)

    def cargarDistrito(self):
        self.cbDistrito.setEnabled(False)

        texto=self.cbProvincia.currentText()
        provincia=texto[texto.find("-")+2:]

        if provincia=="": return

        cbDep=self.cbDep.currentText()
        departamento=cbDep[cbDep.find("-")+2:]

        cbPais=self.cbPais.currentText()
        pais=cbPais[cbPais.find("-")+2:]

        self.cbDistrito.clear()

        codigoDep=""
        codigoPais=""
        for k,v in datos.items():
            codigoDist=k.split("-")
            if v==pais and "-".join(codigoDist[1:])=="00-00-00": codigoPais=codigoDist[0]
            if v==departamento and "-".join(codigoDist[2:])=="00-00" and codigoPais==codigoDist[0]: codigoDep=codigoDist[0:2]
            if v==provincia and "-".join(codigoDist[3:])=="00" and codigoPais==codigoDist[0] and codigoDep==codigoDist[0:2]: codigoProv=codigoDist[0:3]
        for k,v in datos.items():
            codigoDist=k.split("-")
            if codigoDist[3]!="00" and codigoProv==codigoDist[0:3] and codigoDep==codigoDist[0:2] and codigoPais==codigoDist[0]:
                if codigoDist[3]!="00": self.cbDistrito.addItem(codigoDist[3]+" - "+v)
        self.cbDistrito.setCurrentIndex(-1)
        self.leUbigeo.clear()
        self.cbDistrito.setEnabled(True)

    def ubigeo(self):

        cbDistrito=self.cbDistrito.currentText()
        CodDistrito=cbDistrito[0:cbDistrito.find("-")-1]

        cbProvincia=self.cbProvincia.currentText()
        CodProvincia=cbProvincia[0:cbProvincia.find("-")-1]

        cbDep=self.cbDep.currentText()
        CodDepartamento=cbDep[0:cbDep.find("-")-1]

        Ubigeo=CodDepartamento+CodProvincia+CodDistrito

        if len(Ubigeo)!=0:
            self.leUbigeo.setText(Ubigeo)

    def Grabar(self):
        try:
            caso=''
            contador=0
            while len(caso)==0:
                NomreTipoProv=self.cbTipo_Prov.currentText()
                for k,v in TipProv.items():
                    if NomreTipoProv==v:
                        Tipo_Prov=k

                RUC=self.leRUC.text()
                Estado_Prov=self.leEstado_Prov.text()
                Direcc_Prov=self.leDirecc_Prov.text()
                Razon_Social=self.leRazon_Social.text()

                cbPais=self.cbPais.currentText()
                Pais=cbPais[0:cbPais.find("-")-1]

                cbDep=self.cbDep.currentText()
                Departamento=cbDep[0:cbDep.find("-")-1]

                cbProvincia=self.cbProvincia.currentText()
                Provincia=cbProvincia[0:cbProvincia.find("-")-1]

                cbDistrito=self.cbDistrito.currentText()
                Distrito=cbDistrito[0:cbDistrito.find("-")-1]

                Ubigeo=self.leUbigeo.text()

                Telf_Fijo=self.leTelf_Fijo.text()
                Anexo=self.leAnexo.text()
                Fax=self.leFax.text()
                Telf_Cel=self.leTelf_Cel.text()
                Correo_Emp=self.leCorreo_Emp.text()
                Repre_Emp=self.leRepre_Emp.text()
                DNI_Repre=self.leDNI.text()
                Correo_Repre=self.leCorreo_Repre.text()
                Telf_Cel_Repre=self.leTelf_Cel_Repre.text()

                Fecha=datetime.now().strftime("%Y-%m-%d")
                Hora=datetime.now().strftime("%H:%M:%S.%f")

                sqlCodProv="SELECT Cod_actual FROM TAB_SOC_017_Rango_Numero_Catalogo WHERE Tipo_Rango = 4"
                Cod_Actual=convlist(sqlCodProv)
                print(Cod_Actual)

                if Pais=='1':
                    if len(Tipo_Prov) and len(Pais) and len(Direcc_Prov) and len(Departamento) and len(Provincia) and len(Distrito) and (len(Telf_Fijo) or len(Telf_Cel))  and len(Correo_Emp) and len(Repre_Emp) and len(DNI_Repre) and len(Correo_Repre) and len(Telf_Cel_Repre)!=0:
                        sql ='''INSERT INTO TAB_PROV_001_Registro_de_Proveedores (Cod_prov,Razón_social,Tip_Prov,Nro_Telf,Correo,Direcc_prov,Departamento,Provincia,Distrito,País,Ubigeo,Nro_Telf_Emp,Nro_Fax,Anexo,RUC_NIF,Representante,DNI_Repre,Correo_Repre,Telf_Repre,Estado_Prov,Usuario_Reg,Fecha_Reg,Hora_Reg)
                        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''%(Cod_Actual[0],Razon_Social,Tipo_Prov,Telf_Fijo,Correo_Emp,Direcc_Prov,Departamento,Provincia,Distrito,Pais,Ubigeo,Telf_Cel,Fax,Anexo,RUC,Repre_Emp,DNI_Repre,Correo_Repre,Telf_Cel_Repre,Estado_Prov,Cod_Usuario,Fecha,Hora)
                        respuesta=ejecutarSql(sql)
                        if respuesta['respuesta']=='correcto':
                            Cod_Actual[0]=int(Cod_Actual[0])
                            sqlCodActual="UPDATE TAB_SOC_017_Rango_Numero_Catalogo SET Cod_actual='%s' WHERE Tipo_Rango = 4" %(Cod_Actual[0]+1)
                            ejecutarSql(sqlCodActual)
                            mensajeDialogo("informacion", "Información", "Registro guardado")
                            self.leCod_Prov.setText(str(Cod_Actual[0]))
                            self.pbHabilitar.setEnabled(True)
                            self.pbBaja.setEnabled(True)

                            self.cbTipo_Prov.setEnabled(False)
                            self.cbTipo_Prov.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
                            self.leCod_Prov.setReadOnly(True)
                            self.leRUC.setReadOnly(True)
                            self.cbPais.setEnabled(False)
                            self.cbPais.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.cbDep.setEnabled(False)
                            self.cbDep.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.cbProvincia.setEnabled(False)
                            self.cbProvincia.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.cbDistrito.setEnabled(False)
                            self.cbDistrito.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.leUbigeo.setReadOnly(True)
                            self.leTelf_Fijo.setReadOnly(True)
                            self.leAnexo.setReadOnly(True)
                            self.leFax.setReadOnly(True)
                            self.leTelf_Cel.setReadOnly(True)
                            self.leCorreo_Emp.setReadOnly(True)
                            self.leDNI.setReadOnly(True)
                            self.leCorreo_Repre.setReadOnly(True)
                            self.leTelf_Cel_Repre.setReadOnly(True)

                            self.pbGrabar.setEnabled(False)
                            self.pbHabilitar.setEnabled(True)
                            self.pbInterlocutores.setEnabled(True)
                            self.pbBancos.setEnabled(True)
                            self.pbDatos_Compra.setEnabled(True)

                            caso='Algo'
                            contador+=1
                            if contador==5:
                                # respuesta['respuesta']=='incorrecto':
                                mensajeDialogo("error", "Error", "Ingrese Datos Válidos")

                    else:
                        mensajeDialogo("error", "Error", "Faltan Datos")
                        break
                else:
                    if len(Tipo_Prov) and len(Pais) and len(Direcc_Prov) and len(Departamento) and (len(Telf_Fijo) or len(Telf_Cel))  and len(Correo_Emp) and len(Repre_Emp) and len(DNI_Repre) and len(Correo_Repre) and len(Telf_Cel_Repre)!=0:
                        sql ='''INSERT INTO TAB_PROV_001_Registro_de_Proveedores (Cod_prov,Razón_social,Tip_Prov,Nro_Telf,Correo,Direcc_prov,Departamento,Provincia,Distrito,País,Ubigeo,Nro_Telf_Emp,Nro_Fax,Anexo,RUC_NIF,Representante,DNI_Repre,Correo_Repre,Telf_Repre,Estado_Prov,Usuario_Reg,Fecha_Reg,Hora_Reg)
                        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' %(Cod_Actual[0],Razon_Social,Tipo_Prov,Telf_Fijo,Correo_Emp,Direcc_Prov,Departamento,Provincia,Distrito,Pais,Ubigeo,Telf_Cel,Fax,Anexo,RUC,Repre_Emp,DNI_Repre,Correo_Repre,Telf_Cel_Repre,Estado_Prov,Cod_Usuario,Fecha,Hora)
                        respuesta=ejecutarSql(sql)
                        if respuesta['respuesta']=='correcto':
                            mensajeDialogo("informacion", "Información", "Registro guardado")
                            self.leCod_Prov.setText(Cod_Actual[0])
                            self.pbHabilitar.setEnabled(True)
                            self.pbBaja.setEnabled(True)
                            Cod_Actual[0]=int(Cod_Actual[0])
                            sqlCodActual="UPDATE TAB_SOC_017_Rango_Numero_Catalogo SET Cod_actual='%s' WHERE Tipo_Rango = 4" %(Cod_Actual[0]+1)
                            ejecutarSql(sqlCodActual)

                            self.cbTipo_Prov.setEnabled(False)
                            self.cbTipo_Prov.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
                            self.leRUC.setReadOnly(True)
                            self.cbPais.setEnabled(False)
                            self.cbPais.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.cbDep.setEnabled(False)
                            self.cbDep.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.cbProvincia.setEnabled(False)
                            self.cbProvincia.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.cbDistrito.setEnabled(False)
                            self.cbDistrito.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")

                            self.leUbigeo.setReadOnly(True)
                            self.leTelf_Fijo.setReadOnly(True)
                            self.leAnexo.setReadOnly(True)
                            self.leFax.setReadOnly(True)
                            self.leTelf_Cel.setReadOnly(True)
                            self.leCorreo_Emp.setReadOnly(True)
                            self.leDNI.setReadOnly(True)
                            self.leCorreo_Repre.setReadOnly(True)
                            self.leTelf_Cel_Repre.setReadOnly(True)

                            self.pbGrabar.setEnabled(False)
                            self.pbHabilitar.setEnabled(True)
                            self.pbInterlocutores.setEnabled(True)
                            self.pbBancos.setEnabled(True)
                            self.pbDatos_Compra.setEnabled(True)

                            caso='Algo'
                            contador+=1
                            if contador==5:
                                mensajeDialogo("error", "Error", "Ingrese Datos Válido")

                    else:
                        mensajeDialogo("error", "Error", "Faltan Datos")
                        break
        except Exception as e:
            mensajeDialogo("error", "Error", "Campos vacios")
            print(e)

    def Habilitar(self):

        cbPais=self.cbPais.currentText()
        Pais=cbPais[0:cbPais.find("-")-1]
        Dep=self.cbDep.currentText()
        if Pais=='01':
            self.cbDep.setEnabled(True)
            self.cbProvincia.setEnabled(True)
            self.cbDistrito.setEnabled(True)
        else:
            self.cbDep.setEnabled(True)

        llenarDep(datos,self.cbDep,Pais)
        self.cbDep.setCurrentIndex(self.cbDep.findText(Dep))

        self.leTelf_Fijo.setReadOnly(False)
        self.leAnexo.setReadOnly(False)
        self.leFax.setReadOnly(False)
        self.leTelf_Cel.setReadOnly(False)
        self.leCorreo_Emp.setReadOnly(False)
        self.leRepre_Emp.setReadOnly(False)
        self.leDNI.setReadOnly(False)
        self.leCorreo_Repre.setReadOnly(False)
        self.leTelf_Cel_Repre.setReadOnly(False)

        self.pbBaja.setEnabled(False)
        self.pbGrabar.setEnabled(False)
        self.pbModificar.setEnabled(True)


    def Modificar(self):
        try:
            NomreTipoProv=self.cbTipo_Prov.currentText()
            for k,v in TipProv.items():
                if NomreTipoProv==v:
                    Tipo_Prov=k

            RUC=self.leRUC.text()
            Estado_Prov=self.leEstado_Prov.text()
            Direcc_Prov=self.leDirecc_Prov.text()
            Razon_Social=self.leRazon_Social.text()

            cbPais=self.cbPais.currentText()
            Pais=cbPais[0:cbPais.find("-")-1]

            cbDep=self.cbDep.currentText()
            Departamento=cbDep[0:cbDep.find("-")-1]

            cbProvincia=self.cbProvincia.currentText()
            Provincia=cbProvincia[0:cbProvincia.find("-")-1]

            cbDistrito=self.cbDistrito.currentText()
            Distrito=cbDistrito[0:cbDistrito.find("-")-1]

            Ubigeo=self.leUbigeo.text()
            Telf_Fijo=self.leTelf_Fijo.text()
            Anexo=self.leAnexo.text()
            Fax=self.leFax.text()
            Telf_Cel=self.leTelf_Cel.text()
            Correo_Emp=self.leCorreo_Emp.text()
            Repre_Emp=self.leRepre_Emp.text()
            DNI_Repre=self.leDNI.text()
            Correo_Repre=self.leCorreo_Repre.text()
            Telf_Cel_Repre=self.leTelf_Cel_Repre.text()

            Fecha=datetime.now().strftime("%Y-%m-%d")
            Hora=datetime.now().strftime("%H:%M:%S.%f")

            Cod_Prov=self.leCod_Prov.text()
            if len(Cod_Prov)!=0:
                sql ='''UPDATE TAB_PROV_001_Registro_de_Proveedores SET Nro_Telf='%s',Correo='%s',Direcc_prov='%s',Departamento='%s',Provincia='%s',Distrito='%s',Ubigeo='%s',Nro_Telf_Emp='%s',Nro_Fax='%s',Anexo='%s',Representante='%s',DNI_Repre='%s',Correo_Repre='%s',Telf_Repre='%s',Estado_Prov='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s';'''%(Telf_Fijo,Correo_Emp,Direcc_Prov,Departamento,Provincia,Distrito,Ubigeo,Telf_Cel,Fax,Anexo,Repre_Emp,DNI_Repre,Correo_Repre,Telf_Cel_Repre,Estado_Prov,Cod_Usuario,Fecha,Hora,Cod_Prov)
                respuesta=ejecutarSql(sql)
                if respuesta['respuesta']=='correcto':
                    self.pbGrabar.setEnabled(False)
                    self.pbModificar.setEnabled(False)
                    self.pbBaja.setEnabled(True)
                    mensajeDialogo("informacion", "Información", "Registro modificado")

                    self.leEstado_Prov.setReadOnly(True)
                    self.cbDep.setEnabled(False)
                    self.cbDep.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
                    self.cbProvincia.setEnabled(False)
                    self.cbProvincia.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
                    self.cbDistrito.setEnabled(False)
                    self.cbDistrito.setStyleSheet("color: rgb(0,0,0);\n""background-color: rgb(255,255,255);")
                    self.leTelf_Fijo.setReadOnly(True)
                    self.leAnexo.setReadOnly(True)
                    self.leFax.setReadOnly(True)
                    self.leTelf_Cel.setReadOnly(True)
                    self.leCorreo_Emp.setReadOnly(True)
                    self.leRepre_Emp.setReadOnly(True)
                    self.leDNI.setReadOnly(True)
                    self.leCorreo_Repre.setReadOnly(True)
                    self.leTelf_Cel_Repre.setReadOnly(True)


                elif respuesta['respuesta']=='incorrecto':
                    mensajeDialogo("error", "Error", "Ingrese Datos Válidos")

        except Exception as e:
            mensajeDialogo("error", "Error", "No se pudo modificar")
            print(e)

    def DardeBaja(self):

        Estado_Proveedor=self.leEstado_Prov.text()

        if Estado_Proveedor == "1":
            reply = mensajeDialogo("pregunta", "Pregunta","¿Realmente desea DAR BAJA al Proveedor?")
            if reply == 'Yes':
                Cod_Prov=self.leCod_Prov.text()
                Estado_Proveedor='2'

                ModFecha=datetime.now().strftime("%Y-%m-%d")
                ModHora=datetime.now().strftime("%H:%M:%S.%f")

                sql ='''UPDATE TAB_PROV_001_Registro_de_Proveedores SET Estado_Prov='%s', Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_prov='%s';'''%(Estado_Proveedor,Cod_Usuario,ModFecha,ModHora,Cod_Prov)
                respuesta=ejecutarSql(sql)
                sqlInter ='''UPDATE TAB_PROV_002_Registro_de_Interlocutores_del_Proveedor SET Estado_Inter='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s';'''%('2',Cod_Usuario,ModFecha,ModHora,Cod_Prov)
                ejecutarSql(sqlInter)
                sqlBanc ='''UPDATE TAB_PROV_007_Bancos_y_cuentas_del_Proveedor SET Estado_Banco='%s',Usuario_Mod='%s',Fecha_Mod='%s',Hora_Mod='%s' WHERE Cod_Prov='%s';'''%('2',Cod_Usuario,ModFecha,ModHora,Cod_Prov)
                ejecutarSql(sqlBanc)
                if respuesta['respuesta']=='correcto':
                    self.leActivo_Baja.setText("BAJA")
                    self.leActivo_Baja.setStyleSheet("color: rgb(255,0,0);\n""background-color: rgb(255,255,255);")
                    self.leEstado_Prov.setText(Estado_Proveedor)
                    self.pbBaja.setEnabled(False)
                    self.pbModificar.setEnabled(False)
                    self.pbHabilitar.setEnabled(False)
                    self.pbGrabar.setEnabled(False)
                    mensajeDialogo("informacion", "Información", "Proveedor dado de BAJA")
                elif respuesta['respuesta']=='incorrecto':
                    mensajeDialogo("error", "Error", "No se pudo dar de BAJA")

        elif Estado_Proveedor == "2":
            mensajeDialogo("error", "Error", "Proveedor ya fue dado de BAJA")

    def Salir(self):
        self.close()

    def Inter(self):
        Cod_Prov=self.leCod_Prov.text()
        Razon_Social=self.leRazon_Social.text()
        Estado=self.leEstado_Prov.text()
        if Estado=="2":
            self.int=Interlocutores(Cod_Soc,Cod_Usuario,Cod_Prov,Razon_Social)
            self.int.pbGrabar.setEnabled(False)
            self.int.pbHabilitar.setEnabled(False)
            self.int.pbBaja.setEnabled(False)
            self.int.showMaximized()
        else:
            self.int=Interlocutores(Cod_Soc,Cod_Usuario,Cod_Prov,Razon_Social)
            self.int.showMaximized()

    def Ban(self):
        Cod_Prov=self.leCod_Prov.text()
        Razon_Social=self.leRazon_Social.text()
        Estado=self.leEstado_Prov.text()
        if Estado=="2":
            self.ban=Bancos(Cod_Soc,Cod_Usuario,Cod_Prov,Razon_Social)
            self.ban.pbGrabar.setEnabled(False)
            self.ban.pbHabilitar.setEnabled(False)
            self.ban.pbBaja.setEnabled(False)
            self.ban.showMaximized()
        else:
            self.ban=Bancos(Cod_Soc,Cod_Usuario,Cod_Prov,Razon_Social)
            self.ban.showMaximized()

    def Comp(self):
        Cod_Prov=self.leCod_Prov.text()
        Razon_Social=self.leRazon_Social.text()
        Estado=self.leEstado_Prov.text()
        if Estado=="2":
            self.com=Compra(Cod_Soc,Cod_Usuario,Cod_Prov,Razon_Social)
            self.com.pbGrabar.setEnabled(False)
            self.com.pbHabilitar.setEnabled(False)
            self.com.showMaximized()
        else:
            self.com=Compra(Cod_Soc,Cod_Usuario,Cod_Prov,Razon_Social)
            self.com.showMaximized()

    def validarCorreo(self):
        if self.leCorreo_Emp.text()!="":
            validarCorreo(self.leCorreo_Emp)

        if self.leCorreo_Repre.text()!="":
            validarCorreo(self.leCorreo_Repre)

    def validarNumero(self):
        if self.leDNI.text()!="":
            validarNumero(self.leDNI)

if __name__ == '__main__':
    app=QApplication(sys.argv)
    _main=ERP_PPROV_001()
    _main.showMaximized()
    app.exec_()
