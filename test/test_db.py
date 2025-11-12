# petcare/test/test_db.py
from petcare.core.database import SessionLocal
from datetime import date
# importa los modelos ORM
from petcare.domain.models.usuario_model import Usuario as UsuarioModel
from petcare.domain.models.mascota_model import Mascota as MascotaModel
from petcare.domain.models.reserva_model import Reserva as ReservaModel
from petcare.domain.models.resena_model import Resena as ResenaModel
from petcare.domain.models.cuidador_model import Cuidador as CuidadorModel

def run():
    db = SessionLocal()
    try:
        # Crear usuarios (ORM)
        u_cliente = UsuarioModel(
            nombre="Erika",
            email="erika@example.com",
            contrasena_hash="hashed_password_example",
            tipo="cliente"
        )

        u_cuidador = UsuarioModel(
            nombre="María",
            email="maria@example.com",
            contrasena_hash="hashed_password_example",
            tipo="cuidador"
        )

        db.add_all([u_cliente, u_cuidador])
        db.commit()

        # refrescar para obtener los ids que creó la BD
        db.refresh(u_cliente)
        db.refresh(u_cuidador)

        print("✅ Usuarios insertados. IDs:", u_cliente.id, u_cuidador.id)

        # Opcional: crear una mascota (si tenés MascotaDB definido)
        try:
            mascota = MascotaModel(
                nombre="Luna",
                especie="perro",
                raza="mestizo",
                edad=3,
                peso=12.5,
                owner_id=u_cliente.id
            )
            db.add(mascota)
            db.commit()
            db.refresh(mascota)
            print("✅ Mascota creada ID:", mascota.id)
        except Exception as e:
            print("⚠️ No se pudo crear mascota (tal vez no existe MascotaModel):", e)
            db.rollback()

        # Opcional: crear reserva (usa FK a usuarios y mascota)
        try:
            reserva = ReservaModel(
                cliente_id=u_cliente.id,
                cuidador_id=u_cuidador.id,
                mascota_id=mascota.id,
                fecha_inicio=date(2025, 10, 30),  
                fecha_fin=date(2025, 11, 2),
                estado="pendiente"
            )
            db.add(reserva)
            db.commit()
            db.refresh(reserva)
            print("✅ Reserva creada ID:", reserva.id)
        except Exception as e:
            print("⚠️ No se pudo crear reserva:", e)
            db.rollback()

        try: 
            resena = ResenaModel(
            cliente_id=u_cliente.id,
            cuidador_id=u_cuidador.id,
            puntaje=9,
            comentario="Muy buena atención!"
            )
            db.add(resena)
            db.commit()
            db.refresh(resena)
            print("✅ Reseña creada ->", resena.id)
        except Exception as e: 
            print("⚠️ No se pudo crear resena:", e)
            db.rollback()


        # Consultas de verificación
        clientes = db.query(UsuarioModel).filter_by(tipo="cliente").all()
        cuidadores = db.query(UsuarioModel).filter_by(tipo="cuidador").all()

        print("\n📋 Clientes:")
        for c in clientes:
            print(f" - {c.id} {c.nombre} {c.email}")

        print("\n📋 Cuidadores:")
        for cu in cuidadores:
            print(f" - {cu.id} {cu.nombre} {cu.email}")

    finally:
        db.close()

if __name__ == "__main__":
    run()


#Hay correr los codigos asi

#python -m petcare.init_db
#python -m petcare.test.test_db

#Si no funciona y hay un archivo percare.db ejecutar
##rm petcare.db