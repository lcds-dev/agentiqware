#!/usr/bin/env python3
"""
Script para verificar datos en Firestore Native
"""

from google.cloud import firestore

def check_firestore_data():
    """Verificar que los datos existen en firestore-native"""
    
    # Conectar a la base de datos correcta
    db = firestore.Client(database="firestore-native")
    
    print("Verificando datos en firestore-native...")
    
    # Verificar cada colección
    collections = ['users', 'flows', 'executions', 'components', 'templates']
    
    for collection_name in collections:
        try:
            docs = list(db.collection(collection_name).limit(1).stream())
            if docs:
                print(f"OK {collection_name}: {len(docs)} documento(s) encontrado(s)")
                # Mostrar ID del primer documento
                print(f"  - Ejemplo: {docs[0].id}")
            else:
                print(f"NO {collection_name}: Sin documentos")
        except Exception as e:
            print(f"ERROR {collection_name}: Error - {e}")
    
    print("\nURL para acceder a Firestore Native:")
    print("https://console.cloud.google.com/firestore/databases/firestore-native/data?project=agentiqware-prod")

if __name__ == "__main__":
    check_firestore_data()