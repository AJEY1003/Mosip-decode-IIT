from pymongo import MongoClient
from pymongo.errors import PyMongoError
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
from config.settings import Config
import json
import uuid
from datetime import datetime
import hashlib


class MongoStorage:
    """
    MongoDB storage for flexible document storage
    """
    
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client.ocr_db  # Use a specific database name
        self.collection = self.db.ocr_documents
    
    def save_document(self, document_data: Dict[str, Any]) -> str:
        """
        Save document data to MongoDB
        """
        try:
            # Add timestamp and ID
            doc_id = str(uuid.uuid4())
            document_data['_id'] = doc_id
            document_data['created_at'] = datetime.utcnow()
            document_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.insert_one(document_data)
            return str(result.inserted_id)
        except PyMongoError as e:
            raise Exception(f"MongoDB error: {str(e)}")
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document by ID from MongoDB
        """
        try:
            document = self.collection.find_one({'_id': doc_id})
            return document
        except PyMongoError as e:
            raise Exception(f"MongoDB error: {str(e)}")
    
    def update_document(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update document in MongoDB
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': doc_id},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            raise Exception(f"MongoDB error: {str(e)}")
    
    def search_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search documents in MongoDB
        """
        try:
            cursor = self.collection.find(query)
            return list(cursor)
        except PyMongoError as e:
            raise Exception(f"MongoDB error: {str(e)}")


class PostgreSQLStorage:
    """
    PostgreSQL storage for structured reporting
    """
    
    def __init__(self):
        try:
            self.conn = psycopg2.connect(Config.POSTGRES_URI)
            self.connection_available = True
        except psycopg2.Error as e:
            print(f"Warning: PostgreSQL connection failed: {str(e)}")
            print("PostgreSQL storage will be unavailable, using MongoDB only")
            self.connection_available = False
            self.conn = None
    
    def create_tables(self):
        """
        Create necessary tables if they don't exist
        """
        if not self.connection_available:
            print("PostgreSQL not available, skipping table creation")
            return
            
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ocr_results (
            id SERIAL PRIMARY KEY,
            document_id VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            dob DATE,
            id_number VARCHAR(255),
            address TEXT,
            document_type VARCHAR(100),
            confidence NUMERIC(3,2),
            status VARCHAR(50),
            extracted_fields JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS ocr_processing_log (
            id SERIAL PRIMARY KEY,
            document_id VARCHAR(255),
            processing_step VARCHAR(100),
            status VARCHAR(50),
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_table_query)
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Error creating tables: {str(e)}")
    
    def save_document(self, document_data: Dict[str, Any]) -> int:
        """
        Save document data to PostgreSQL
        """
        if not self.connection_available:
            print("PostgreSQL not available, skipping save")
            return -1  # Return -1 to indicate failure
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Extract fields for individual columns
                name = document_data.get('extracted_fields', {}).get('name', '')
                dob = document_data.get('extracted_fields', {}).get('dob', None)
                id_number = document_data.get('extracted_fields', {}).get('id_number', '')
                address = document_data.get('extracted_fields', {}).get('address', '')
                doc_type = document_data.get('extracted_fields', {}).get('document_type', '')
                confidence = document_data.get('confidence', 0.0)
                status = document_data.get('status', 'processed')
                
                # Convert date string to date object if needed
                if isinstance(dob, str):
                    from datetime import datetime
                    try:
                        dob = datetime.strptime(dob, '%Y-%m-%d').date()
                    except ValueError:
                        dob = None
                
                # Insert the record
                insert_query = """
                INSERT INTO ocr_results 
                (document_id, name, dob, id_number, address, document_type, confidence, status, extracted_fields)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) 
                DO UPDATE SET
                    name = EXCLUDED.name,
                    dob = EXCLUDED.dob,
                    id_number = EXCLUDED.id_number,
                    address = EXCLUDED.address,
                    document_type = EXCLUDED.document_type,
                    confidence = EXCLUDED.confidence,
                    status = EXCLUDED.status,
                    extracted_fields = EXCLUDED.extracted_fields,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
                """
                
                cur.execute(insert_query, (
                    document_data.get('_id', str(uuid.uuid4())),
                    name,
                    dob,
                    id_number,
                    address,
                    doc_type,
                    confidence,
                    status,
                    json.dumps(document_data.get('extracted_fields', {}))
                ))
                
                result = cur.fetchone()
                self.conn.commit()
                
                return result['id']
                
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"PostgreSQL error: {str(e)}")
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document by ID from PostgreSQL
        """
        if not self.connection_available:
            print("PostgreSQL not available, returning None")
            return None
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM ocr_results WHERE document_id = %s", 
                    (doc_id,)
                )
                result = cur.fetchone()
                
                if result:
                    return dict(result)
                return None
                
        except psycopg2.Error as e:
            raise Exception(f"PostgreSQL error: {str(e)}")
    
    def update_document_status(self, doc_id: str, status: str) -> bool:
        """
        Update document status in PostgreSQL
        """
        if not self.connection_available:
            print("PostgreSQL not available, update failed")
            return False
            
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "UPDATE ocr_results SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE document_id = %s",
                    (status, doc_id)
                )
                self.conn.commit()
                return cur.rowcount > 0
                
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"PostgreSQL error: {str(e)}")
    
    def search_documents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search documents in PostgreSQL with filters
        """
        if not self.connection_available:
            print("PostgreSQL not available, returning empty list")
            return []
            
        try:
            # Build dynamic query based on filters
            conditions = []
            values = []
            
            for key, value in filters.items():
                if key in ['name', 'id_number', 'document_type', 'status']:
                    conditions.append(f"{key} ILIKE %s")
                    values.append(f"%{value}%")
                elif key == 'confidence_min':
                    conditions.append("confidence >= %s")
                    values.append(value)
                elif key == 'confidence_max':
                    conditions.append("confidence <= %s")
                    values.append(value)
            
            query = "SELECT * FROM ocr_results"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values)
                results = cur.fetchall()
                
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            raise Exception(f"PostgreSQL error: {str(e)}")
    
    def log_processing_step(self, document_id: str, step: str, status: str, error_message: str = None):
        """
        Log processing steps for audit trail
        """
        if not self.connection_available:
            print("PostgreSQL not available, skipping log")
            return
            
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO ocr_processing_log (document_id, processing_step, status, error_message) VALUES (%s, %s, %s, %s)",
                    (document_id, step, status, error_message)
                )
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"PostgreSQL error: {str(e)}")


class DataStorageManager:
    """
    Manager class to handle both MongoDB and PostgreSQL storage
    """
    
    def __init__(self):
        self.mongo_storage = MongoStorage()
        self.postgres_storage = PostgreSQLStorage()
        if self.postgres_storage.connection_available:
            self.postgres_storage.create_tables()
    
    def save_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save document to both MongoDB and PostgreSQL
        """
        # Add a unique document ID if not present
        if '_id' not in document_data:
            document_data['_id'] = str(uuid.uuid4())
        
        # Save to MongoDB (flexible storage)
        mongo_id = self.mongo_storage.save_document(document_data.copy())
        
        # Save to PostgreSQL (structured storage)
        postgres_id = self.postgres_storage.save_document(document_data)
        
        return {
            'mongo_id': mongo_id,
            'postgres_id': postgres_id,
            'document_id': document_data['_id']
        }
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document from both storages
        """
        # Get from PostgreSQL (structured)
        pg_doc = self.postgres_storage.get_document(doc_id)
        
        # Get from MongoDB (flexible)
        mongo_doc = self.mongo_storage.get_document(doc_id)
        
        if pg_doc and mongo_doc:
            # Combine the data
            result = pg_doc.copy()
            result['full_data'] = mongo_doc
            return result
        elif pg_doc:
            return pg_doc
        elif mongo_doc:
            return mongo_doc
        else:
            return None
    
    def update_document_status(self, doc_id: str, status: str) -> bool:
        """
        Update document status in PostgreSQL
        """
        return self.postgres_storage.update_document_status(doc_id, status)
    
    def search_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search documents in PostgreSQL
        """
        return self.postgres_storage.search_documents(query)
    
    def log_processing_step(self, document_id: str, step: str, status: str, error_message: str = None):
        """
        Log processing step
        """
        self.postgres_storage.log_processing_step(document_id, step, status, error_message)


# Example usage
if __name__ == "__main__":
    # Example usage
    storage_manager = DataStorageManager()
    
    sample_doc = {
        "document_type": "Aadhaar",
        "extracted_fields": {
            "name": "Ramesh Kumar",
            "dob": "1999-04-12",
            "id_number": "123456789012",
            "address": "123 Main Street, City, State"
        },
        "confidence": 0.98,
        "status": "approved"
    }
    
    result = storage_manager.save_document(sample_doc)
    print("Saved document with IDs:", result)
    
    retrieved = storage_manager.get_document(result['document_id'])
    print("Retrieved document:", retrieved)