"""Police Complaints & Misconduct Data Extractor

This module extracts and processes police misconduct data including bribery,
extortion, custodial deaths, false arrests, and abuse of power cases.
"""

import pandas as pd
import logging
from typing import Dict, List, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class BaseTransformer:
    """Base class for data transformers"""
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data into structured format"""
        raise NotImplementedError
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate transformed data"""
        raise NotImplementedError


class PoliceComplaintsTransformer(BaseTransformer):
    """Transformer for Police complaints and misconduct data"""
    
    REQUIRED_COLUMNS = [
        'complaint_id', 'officer_name', 'officer_rank', 'station',
        'complaint_type', 'severity', 'date_filed', 'status'
    ]
    
    COMPLAINT_TYPES = [
        'BRIBERY', 'EXTORTION', 'CUSTODIAL_DEATH', 'TORTURE',
        'FALSE_ARREST', 'ABUSE_OF_POWER', 'ILLEGAL_DETENTION',
        'ENCOUNTER_KILLING', 'EVIDENCE_TAMPERING', 'HARASSMENT'
    ]
    
    SEVERITY_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    
    OFFICER_RANKS = [
        'CONSTABLE', 'HEAD_CONSTABLE', 'SUB_INSPECTOR', 'INSPECTOR',
        'DEPUTY_SP', 'SP', 'DIG', 'IG', 'DGP'
    ]
    
    def __init__(self):
        self.stats = {
            'total_complaints': 0,
            'critical_cases': 0,
            'complaints_by_type': {},
            'complaints_by_rank': {},
            'complaints_by_station': {}
        }
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform Police complaints data"""
        logger.info("Starting Police complaints data transformation")
        
        df = data.copy()
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Apply transformations
        df = self._clean_complaint_ids(df)
        df = self._standardize_officer_names(df)
        df = self._categorize_complaints(df)
        df = self._standardize_ranks(df)
        df = self._parse_dates(df)
        df = self._assess_severity(df)
        df = self._extract_station_info(df)
        df = self._categorize_risk(df)
        df = self._calculate_quality_score(df)
        
        self._update_stats(df)
        
        logger.info(f"Transformation complete. Processed {len(df)} complaints")
        return df
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate Police complaints data"""
        missing_cols = set(self.REQUIRED_COLUMNS) - set(data.columns)
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        critical_nulls = data[['complaint_id', 'officer_name', 'complaint_type']].isnull().any()
        if critical_nulls.any():
            logger.warning("Found null values in critical fields")
            return False
        
        return True
    
    def _clean_complaint_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize complaint IDs"""
        if 'complaint_id' in df.columns:
            df['complaint_id'] = df['complaint_id'].astype(str).str.strip().str.upper()
            df = df.drop_duplicates(subset=['complaint_id'], keep='first')
        return df
    
    def _standardize_officer_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize officer names"""
        if 'officer_name' in df.columns:
            df['officer_name'] = df['officer_name'].str.strip().str.title()
        return df
    
    def _categorize_complaints(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize complaints by type"""
        if 'complaint_type' not in df.columns and 'description' in df.columns:
            df['complaint_type'] = df['description'].apply(self._detect_complaint_type)
        return df
    
    def _detect_complaint_type(self, description: str) -> str:
        """Detect complaint type from description"""
        desc_lower = str(description).lower()
        
        if any(word in desc_lower for word in ['bribe', 'money', 'payment']):
            return 'BRIBERY'
        elif any(word in desc_lower for word in ['extort', 'threaten', 'demand']):
            return 'EXTORTION'
        elif any(word in desc_lower for word in ['custodial death', 'custody death', 'died in custody']):
            return 'CUSTODIAL_DEATH'
        elif any(word in desc_lower for word in ['torture', 'beat', 'assault']):
            return 'TORTURE'
        elif any(word in desc_lower for word in ['false arrest', 'wrongful arrest', 'illegal arrest']):
            return 'FALSE_ARREST'
        elif any(word in desc_lower for word in ['abuse of power', 'misuse of authority']):
            return 'ABUSE_OF_POWER'
        elif any(word in desc_lower for word in ['illegal detention', 'unlawful detention']):
            return 'ILLEGAL_DETENTION'
        elif any(word in desc_lower for word in ['encounter', 'fake encounter']):
            return 'ENCOUNTER_KILLING'
        elif any(word in desc_lower for word in ['evidence', 'tamper', 'destroy']):
            return 'EVIDENCE_TAMPERING'
        elif any(word in desc_lower for word in ['harass', 'intimidate']):
            return 'HARASSMENT'
        else:
            return 'OTHER'
    
    def _standardize_ranks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize officer ranks"""
        if 'officer_rank' in df.columns:
            df['officer_rank'] = df['officer_rank'].str.upper().str.strip()
            
            # Normalize rank names
            rank_mapping = {
                'CONST': 'CONSTABLE',
                'HC': 'HEAD_CONSTABLE',
                'SI': 'SUB_INSPECTOR',
                'INSP': 'INSPECTOR',
                'DSP': 'DEPUTY_SP'
            }
            
            df['officer_rank'] = df['officer_rank'].replace(rank_mapping)
        
        return df
    
    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and standardize dates"""
        date_columns = ['date_filed', 'date_incident', 'date_resolved']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _assess_severity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assess complaint severity"""
        def get_severity(complaint_type: str) -> str:
            critical_types = ['CUSTODIAL_DEATH', 'ENCOUNTER_KILLING', 'TORTURE']
            high_types = ['FALSE_ARREST', 'ILLEGAL_DETENTION', 'EXTORTION']
            medium_types = ['BRIBERY', 'EVIDENCE_TAMPERING', 'ABUSE_OF_POWER']
            
            if complaint_type in critical_types:
                return 'CRITICAL'
            elif complaint_type in high_types:
                return 'HIGH'
            elif complaint_type in medium_types:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        if 'severity' not in df.columns:
            df['severity'] = df['complaint_type'].apply(get_severity)
        
        return df
    
    def _extract_station_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and standardize station information"""
        if 'station' in df.columns:
            df['station'] = df['station'].str.strip().str.title()
            
            # Extract district if available
            if 'district' not in df.columns:
                df['district'] = df['station'].str.extract(r'(\w+)\s+Police', expand=False)
        
        return df
    
    def _categorize_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize cases by risk level"""
        def get_risk_level(row) -> str:
            severity = row.get('severity', 'LOW')
            rank = row.get('officer_rank', '')
            
            high_ranks = ['SP', 'DIG', 'IG', 'DGP', 'DEPUTY_SP']
            
            if severity == 'CRITICAL':
                return 'CRITICAL'
            elif severity == 'HIGH' or rank in high_ranks:
                return 'HIGH'
            elif severity == 'MEDIUM':
                return 'MEDIUM'
            else:
                return 'LOW'
        
        df['risk_level'] = df.apply(get_risk_level, axis=1)
        return df
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate data quality score"""
        def calculate_score(row) -> float:
            score = 1.0
            
            if pd.isna(row.get('complaint_id')):
                score -= 0.3
            if pd.isna(row.get('officer_name')):
                score -= 0.3
            if pd.isna(row.get('station')):
                score -= 0.2
            if pd.isna(row.get('date_filed')):
                score -= 0.2
            
            return max(0.0, score)
        
        df['data_quality_score'] = df.apply(calculate_score, axis=1)
        return df
    
    def _update_stats(self, df: pd.DataFrame):
        """Update extraction statistics"""
        self.stats['total_complaints'] = len(df)
        self.stats['critical_cases'] = len(df[df['severity'] == 'CRITICAL'])
        self.stats['complaints_by_type'] = df['complaint_type'].value_counts().to_dict()
        
        if 'officer_rank' in df.columns:
            self.stats['complaints_by_rank'] = df['officer_rank'].value_counts().to_dict()
        
        if 'station' in df.columns:
            self.stats['complaints_by_station'] = df['station'].value_counts().head(10).to_dict()
    
    def get_stats(self) -> Dict:
        """Get extraction statistics"""
        return self.stats


if __name__ == "__main__":
    logger.info("Police Complaints Extractor Initialized")
    logger.info("Tracks: Bribery, Extortion, Custodial Deaths, False Arrests, Abuse of Power")
    logger.info("Detects: Police misconduct, corruption, human rights violations")
