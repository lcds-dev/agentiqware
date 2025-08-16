#!/usr/bin/env python3
"""
Script para verificar si existe la colección 'components' en Firestore
"""

import os
import sys
from google.cloud import firestore

def check_components_collection():
    """Verificar si existe la colección components y mostrar su contenido"""
    try:
        # Inicializar cliente de Firestore
        db = firestore.Client()
        
        # Obtener referencia a la colección components
        components_ref = db.collection('components')
        
        print("Verificando coleccion 'components' en Firestore...")
        
        # Intentar obtener todos los documentos
        docs = components_ref.stream()
        
        components = []
        for doc in docs:
            components.append({
                'id': doc.id,
                'data': doc.to_dict()
            })
        
        if components:
            print(f"EXITO: Coleccion 'components' encontrada con {len(components)} documentos:")
            print("="*60)
            
            for comp in components:
                print(f"ID: {comp['id']}")
                print(f"Datos: {comp['data']}")
                print("-"*40)
                
        else:
            print("ADVERTENCIA: Coleccion 'components' existe pero esta vacia")
            print("\nSugerencia: Puede que necesites crear los componentes base")
            
    except Exception as e:
        print(f"ERROR al acceder a Firestore: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verificar que las credenciales de Google Cloud esten configuradas")
        print("2. Ejecutar: gcloud auth application-default login")
        print("3. Verificar que el proyecto tenga Firestore habilitado")
        
        return False
    
    return True

if __name__ == "__main__":
    check_components_collection()