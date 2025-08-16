#!/usr/bin/env python3
"""
Script para crear datos de prueba en Firestore Native
"""

import os
from datetime import datetime
from google.cloud import firestore

# Inicializar cliente con la nueva base de datos
db = firestore.Client(database="firestore-native")

def create_test_data():
    """Crear documentos de prueba en todas las colecciones"""
    
    print("Creando datos de prueba en Firestore Native...")
    
    # 1. Crear usuario de prueba
    user_data = {
        'user_id': 'test_user_001',
        'email': 'test@agentiqware.com',
        'name': 'Usuario de Prueba',
        'created_at': datetime.utcnow().isoformat(),
        'subscription': 'free',
        'limits': {
            'flows': 5,
            'executions_per_day': 100,
            'storage_gb': 1
        }
    }
    db.collection('users').document('test_user_001').set(user_data)
    print("OK Usuario creado")
    
    # 2. Crear flujo de prueba
    flow_data = {
        'id': 'test_flow_001',
        'name': 'Flujo de Prueba - Automatización Excel',
        'user_id': 'test_user_001',
        'created_at': datetime.utcnow().isoformat(),
        'description': 'Flujo de prueba para lectura y procesamiento de Excel',
        'status': 'active',
        'nodes': [
            {
                'id': 'node_1',
                'type': 'excel_reader',
                'name': 'Leer Excel',
                'position': {'x': 100, 'y': 100},
                'data': {
                    'excel_file_name': 'datos.xlsx',
                    'sheet_name': 'Hoja1',
                    'destination': 'excel_data'
                }
            },
            {
                'id': 'node_2',
                'type': 'condition',
                'name': 'Validar Datos',
                'position': {'x': 300, 'y': 100},
                'data': {
                    'left_value': '${excel_data.rows}',
                    'operator': '>',
                    'right_value': '0'
                }
            }
        ],
        'connections': [
            {
                'from': 'node_1',
                'to': 'node_2',
                'fromOutput': 'default',
                'toInput': 'default'
            }
        ]
    }
    db.collection('flows').document('test_flow_001').set(flow_data)
    print("OK Flujo creado")
    
    # 3. Crear ejecución de prueba
    execution_data = {
        'execution_id': 'exec_test_001',
        'flow_id': 'test_flow_001',
        'user_id': 'test_user_001',
        'status': 'completed',
        'start_time': datetime.utcnow().isoformat(),
        'end_time': datetime.utcnow().isoformat(),
        'nodes_executed': 2,
        'execution_history': [
            {
                'node_id': 'node_1',
                'node_type': 'excel_reader',
                'timestamp': datetime.utcnow().isoformat(),
                'result': {'status': 'success', 'rows': 150, 'columns': 5}
            }
        ],
        'variables': {
            'excel_data': {'rows': 150, 'columns': 5}
        }
    }
    db.collection('executions').document('exec_test_001').set(execution_data)
    print("OK Ejecución creada")
    
    # 4. Crear componente de prueba
    component_data = {
        'id': 'excel_reader',
        'name': 'Lector de Excel',
        'category': 'Datos',
        'description': 'Lee archivos Excel y los convierte en DataFrames',
        'config': {
            'fields': [
                {'name': 'excel_file_name', 'type': 'string', 'required': True},
                {'name': 'sheet_name', 'type': 'string', 'default': 'Sheet1'},
                {'name': 'destination', 'type': 'string', 'required': True}
            ]
        },
        'executor_class': 'ExcelReaderExecutor',
        'version': '1.0.0',
        'created_at': datetime.utcnow().isoformat()
    }
    db.collection('components').document('excel_reader').set(component_data)
    print("OK Componente creado")
    
    # 5. Crear plantilla de flujo
    template_data = {
        'id': 'template_excel_automation',
        'name': 'Automatización de Excel',
        'category': 'Datos',
        'description': 'Plantilla para automatizar procesamiento de archivos Excel',
        'tags': ['excel', 'datos', 'automatización'],
        'template_data': flow_data,
        'created_at': datetime.utcnow().isoformat(),
        'downloads': 0,
        'rating': 4.5
    }
    db.collection('templates').document('template_excel_automation').set(template_data)
    print("OK Plantilla creada")
    
    print("\nDatos de prueba creados exitosamente!")
    print("\nAhora puedes ver las colecciones en:")
    print("https://console.cloud.google.com/firestore/data?project=agentiqware-prod&database=firestore-native")
    print("\nColecciones creadas:")
    print("- users (1 documento)")
    print("- flows (1 documento)")
    print("- executions (1 documento)")
    print("- components (1 documento)")
    print("- templates (1 documento)")

if __name__ == "__main__":
    create_test_data()