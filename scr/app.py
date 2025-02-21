from flask import Flask,jsonify,request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity

app=Flask(__name__)
    
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_USER']='root'
app.config['MYSQL_DB']='hoys_cine'

conex=MySQL(app)
app.config["JWT_SECRET_KEY"]="secreto"
jwt=JWTManager(app)

#print("JWT_SECREY_KEY:", app.config["JWT_SECREY_KEY"])

@app.route('/login',methods=['POST'])
def login():
    data=request.json
    user=data.get('user')
    password=data.get('password')
    #simulacion de login
    if user=="nico" and password=="123":
        access_token=create_access_token(identity=user)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"Mensaje":"Usuario o contraseña incorrecta"}),401
    

    
    
@app.route('/peliculas',methods=['GET'])
@jwt_required()
def peliculas():
    try:
        user=get_jwt_identity()
        with conex.connection.cursor() as cursor:
            sql="""SELECT * FROM peliculas
            """
            cursor.execute(sql)
            data=cursor.fetchall()
            peliculas=[]
            for fila in data:
                pelicula={"ID":fila[0],"Titulo":fila[1],"Genero":fila[2],"IDcompania":fila[3],"Año Estreno":fila[4]}
                peliculas.append(pelicula)
            return jsonify({"peliculas":peliculas,"Mensaje":"Cursos Listados"}),200
        return jsonify({"Mensaje":f"Bienveniedo{user} Aqui estan las peliculas listadas"})
    except Exception as ex:
        return jsonify({ "Mensaje":"Error" }),404
    
@app.route('/peliculas/<int:id>',methods=['GET'])
@jwt_required()
def movie(id):
    try:
        with conex.connection.cursor() as cursor:
            sql="""SELECT id,titulo,genero,idcompania,añoestreno FROM peliculas WHERE id=%s
            """
            cursor.execute(sql,(id,))
            pelicula=cursor.fetchone()
            if pelicula:
                registro={
                    "ID":pelicula[0],
                    "Titulo":pelicula[1],
                    "Genero":pelicula[2],
                    "IDcompania":pelicula[3],
                    "Año Estreno":pelicula[4]
                }
                return jsonify({"Pelicula":registro,"Mensaje":"pelicula Listada"}),200
            else:
                return jsonify({"Mensaje":"Pelicula no Encontrada"}),404
    except Exception as ex:
        return jsonify({ "Mensaje":"Error" }),500
    

@app.route('/peliculas/<int:id>',methods=['DELETE'])
@jwt_required()
def eliminar(id):
    try:
        with conex.connection.cursor() as cursor:
            sql_boletos="""DELETE FROM boletos WHERE pelicula=%s
            """
            cursor.execute(sql_boletos,(id,))
            sql="""DELETE FROM peliculas WHERE id=%s
            """
            cursor.execute(sql,(id,))
            conex.connection.commit()
            if cursor.rowcount > 0:
                return jsonify({"Mensaje":"Pelicula eliminada"}),200
            else:
                return jsonify({"Mensaje":"Pelicula no encontrada"}),404
    except Exception as ex:
        return jsonify({ "Mensaje":"Error","Detalle":str(ex)}),500
    
@app.route('/peliculas',methods=['POST'])
@jwt_required()
def insertar():
    try:
        data=request.json
        id=data.get('id')
        titulo=data.get('titulo')
        genero=data.get('genero')
        idcompania=data.get('idcompania')
        añoestreno= data.get('añoestreno')
        with conex.connection.cursor() as cursor:
            sql="""INSERT INTO peliculas(id,titulo,genero,idcompania,añoestreno)
                VALUES (%s,%s,%s,%s,%s)"""
            cursor.execute(sql,(id,titulo,genero,idcompania,añoestreno))
            conex.connection.commit()
            return jsonify({'Mensaje':"Pelicula registrada"}),200
    except Exception as error:
        return jsonify({"Mensaje":"Error","Detalle":str(error)}),404
    
        
@app.route('/peliculas/<int:id>',methods=['PUT'])
@jwt_required()
def modificar(id):
    data=request.json
    titulo=data.get('titulo')
    genero=data.get('genero')
    idcompania=data.get('idcompania')
    añoestreno=data.get('añoestreno')
    try:
        with conex.connection.cursor() as cursor:
            sql="""UPDATE peliculas 
                SET titulo=%s,genero=%s,idcompania=%s,añoestreno=%s
                WHERE id=%s"""
            cursor.execute(sql,(titulo,genero,idcompania,añoestreno,id))
            conex.connection.commit() 
            return jsonify({"Mensaje":"Pelicula modificada correctamente"}),200
    except Exception as error:
        return jsonify({"Mensaje":"Error al modificar pelicula","Detalles":str(error)}),404
            
        


if __name__=='__main__':
    app.run(debug=True)
    