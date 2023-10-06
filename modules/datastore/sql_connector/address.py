from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation
from modules.datastore.schema import AddressIn, AddressOut, AddressDelete
from fastapi import HTTPException

class SqlAddress(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def create(self, address: AddressIn):
        try:
            data = Address(
                name = address.name,
                location = address.location,
                latitude = address.latitude,
                longitude = address.longitude,
                note = address.note,
                color = address.color,
                address = address.address,
            )
            with self.sessions.begin() as session:
                session.add(data)
                session.flush()
                session.refresh(data)
                result = AddressOut(
                    id = data.id,
                    **address.dict()
                )
                return result
        except:
            raise HTTPException(
                status_code=500,
                detail="Database unknown error"
            )

    def update(self, address_data: AddressIn):
        """
        Update address. If address does not exist, create it.
        """
        try:
            with self.sessions.begin() as session:
                address = session.query(Address).filter(Address.address == address_data.address).first()
                if address is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Address not found"
                    )
                else:
                    for key, value in address_data:
                        setattr(address, key, value)
                #Return updated data
                updated_data = AddressOut(
                    id = address.id,
                    name = address.name,
                    location = address.location,
                    latitude = address.latitude,
                    longitude = address.longitude,
                    note = address.note,
                    running = address.runing,
                    color = address.color,
                    address = address.address, 
                )
                return updated_data
        except:
            raise HTTPException(
                status_code=500,
                detail="Database unknown error"
            )

    def delete(self, address_data: AddressDelete):
        """
        Delete address if exists - according ip address
        """
        try:
            with self.sessions.begin() as session:
                address = session.query(Address).filter(Address.address == address_data.address).first()
                if address is None:
                    raise HTTPException(
                            status_code=400,
                            detail="Address not found"
                    )
                else:
                    session.delete(address)
        except:
            raise HTTPException(
                status_code=500,
                detail="Database unknown error"
            )
    
    def get(self, address):
        """
        Get information about IP address
        """
        try:
            with self.sessions.begin() as session:
                address = session.query(Address).filter(Address.address == address).first()
                if address is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Address not found",
                    )
                    return {"status": "500"}
                else:
                    print(address.color)
                    address_result = AddressOut(
                        id = address.id,
                        address = address.address,
                        name = address.name,
                        location = address.location,
                        latitude = address.latitude,
                        longitude = address.longitude,
                        note = address.note,
                        color = address.color,
                        running= address.runing
                    )
                    return address_result
        except:
            raise HTTPException(
                status_code=500,
                detail="Database unknown error"
            )

    def get_all(self):
        """
        Return all addresses
        """
        try:
            with self.sessions.begin() as session:
                query = session.query(Address)

                address_result = [AddressOut(
                        id = address.id,
                        address = address.address,
                        name = address.name,
                        location = address.location,
                        latitude = address.latitude,
                        longitude = address.longitude,
                        note = address.note,
                        color = address.color,
                        running= address.runing
                    ) for address in query]
                return address_result
        except:
            raise HTTPException(
                status_code=500,
                detail="Database unknown error"
            )
 #           return {"status": "200", "data": [item.values() for item in query.all()]}
