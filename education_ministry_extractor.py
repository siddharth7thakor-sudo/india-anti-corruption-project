"""Education Ministry Corruption Data Extractor

This module extracts and processes corruption-related data from the Ministry of Education,
including scholarship fraud, fake degree mills, examination malpractices, and education fund
misappropriation cases.
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


class EducationMinistryTransformer(BaseTransformer):
    """Transformer for Education Ministry corruption data"""
    
    REQUIRED_COLUMNS = [
        'case_id', 'institution_name', 'institution_type', 'case_type',
        'amount_involved', 'date_reported', 'status', 'officials_involved'
    ]
    
    CASE_TYPES = [
        'SCHOLARSHIP_FRAUD', 'FAKE_DEGREES', 'EXAMINATION_MALPRACTICE',
        'FUND_MISAPPROPRIATION', 'ADMISSION_BRIBERY', 'INFRASTRUCTURE_SCAM',
        'TEACHER_RECRUITMENT_FRAUD', 'TEXTBOOK_PROCUREMENT_SCAM'
    ]
    
    INSTITUTION_TYPES = [
        'UNIVERSITY', 'COLLEGE', 'SCHOOL', 'RESEARCH_INSTITUTE',
        'EXAMINATION_BOARD', 'SCHOLARSHIP_BOARD'
    ]
    
    def __init__(self):
        self.stats = {
            'total_cases': 0,
            'high_value_cases': 0,
            'cases_by_type': {},
            'cases_by_institution': {}
        }
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform Education Ministry data"""
        logger.info("Starting Education Ministry data transformation")
        
        # Create a copy
        df = data.copy()
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Apply transformations
        df = self._clean_case_ids(df)
        df = self._standardize_institution_names(df)
        df = self._categorize_case_types(df)
        df = self._parse_amounts(df)
        df = self._parse_dates(df)
        df = self._extract_officials(df)
        df = self._categorize_risk(df)
        df = self._calculate_quality_score(df)
        
        # Update statistics
        self._update_stats(df)
        
        logger.info(f"Transformation complete. Processed {len(df)} cases")
        return df
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate Education Ministry data"""
        # Check required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(data.columns)
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        # Check for null values in critical fields
        critical_nulls = data[['case_id', 'institution_name', 'case_type']].isnull().any()
        if critical_nulls.any():
            logger.warning("Found null values in critical fields")
            return False
        
        # Validate case types
        invalid_types = ~data['case_type'].isin(self.CASE_TYPES)
        if invalid_types.any():
            logger.warning(f"Found {invalid_types.sum()} invalid case types")
        
        return True
    
    def _clean_case_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize case IDs"""
        if 'case_id' in df.columns:
            df['case_id'] = df['case_id'].astype(str).str.strip().str.upper()
            # Remove duplicates
            df = df.drop_duplicates(subset=['case_id'], keep='first')
        return df
    
    def _standardize_institution_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize institution names"""
        if 'institution_name' in df.columns:
            df['institution_name'] = df['institution_name'].str.strip()
            df['institution_name'] = df['institution_name'].str.title()
            
            # Extract institution type if not present
            if 'institution_type' not in df.columns:
                df['institution_type'] = df['institution_name'].apply(self._detect_institution_type)
        
        return df
    
    def _detect_institution_type(self, name: str) -> str:
        """Detect institution type from name"""
        name_lower = str(name).lower()
        
        if any(word in name_lower for word in ['university', 'varsity']):
            return 'UNIVERSITY'
        elif any(word in name_lower for word in ['college', 'polytechnic']):
            return 'COLLEGE'
        elif any(word in name_lower for word in ['school', 'academy']):
            return 'SCHOOL'
        elif 'research' in name_lower:
            return 'RESEARCH_INSTITUTE'
        elif 'board' in name_lower and 'exam' in name_lower:
            return 'EXAMINATION_BOARD'
        elif 'scholarship' in name_lower:
            return 'SCHOLARSHIP_BOARD'
        else:
            return 'OTHER'
    
    def _categorize_case_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize cases by type"""
        if 'case_type' not in df.columns and 'description' in df.columns:
            df['case_type'] = df['description'].apply(self._detect_case_type)
        
        return df
    
    def _detect_case_type(self, description: str) -> str:
        """Detect case type from description"""
        desc_lower = str(description).lower()
        
        if any(word in desc_lower for word in ['scholarship', 'stipend']):
            return 'SCHOLARSHIP_FRAUD'
        elif any(word in desc_lower for word in ['degree', 'certificate', 'fake']):
            return 'FAKE_DEGREES'
        elif any(word in desc_lower for word in ['exam', 'test', 'paper leak']):
            return 'EXAMINATION_MALPRACTICE'
        elif any(word in desc_lower for word in ['fund', 'grant', 'budget']):
            return 'FUND_MISAPPROPRIATION'
        elif any(word in desc_lower for word in ['admission', 'seat', 'capitation']):
            return 'ADMISSION_BRIBERY'
        elif any(word in desc_lower for word in ['building', 'construction', 'infrastructure']):
            return 'INFRASTRUCTURE_SCAM'
        elif any(word in desc_lower for word in ['teacher', 'faculty', 'recruitment']):
            return 'TEACHER_RECRUITMENT_FRAUD'
        elif any(word in desc_lower for word in ['textbook', 'book', 'procurement']):
            return 'TEXTBOOK_PROCUREMENT_SCAM'
        else:
            return 'OTHER'
    
    def _parse_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and standardize monetary amounts"""
        if 'amount_involved' in df.columns:
            df['amount_involved'] = df['amount_involved'].apply(self._convert_to_numeric)
        
        return df
    
    def _convert_to_numeric(self, amount: Any) -> float:
        """Convert amount string to numeric value"""
        if pd.isna(amount):
            return 0.0
        
        amount_str = str(amount).upper().replace(',', '').strip()
        
        # Handle Indian numbering system
        multipliers = {
            'CRORE': 10000000,
            'CR': 10000000,
            'LAKH': 100000,
            'L': 100000,
            'THOUSAND': 1000,
            'K': 1000
        }
        
        for word, multiplier in multipliers.items():
            if word in amount_str:
                try:
                    number = float(re.findall(r'[\d.]+', amount_str)[0])
                    return number * multiplier
                except (IndexError, ValueError):
                    pass
        
        # Try direct conversion
        try:
            return float(re.findall(r'[\d.]+', amount_str)[0])
        except (IndexError, ValueError):
            return 0.0
    
    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and standardize dates"""
        date_columns = ['date_reported', 'date_detected', 'date_filed']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _extract_officials(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and count officials involved"""
        if 'officials_involved' in df.columns:
            df['official_count'] = df['officials_involved'].apply(
                lambda x: len(str(x).split(',')) if pd.notna(x) else 0
            )
        
        return df
    
    def _categorize_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize cases by risk level"""
        def get_risk_level(row) -> str:
            amount = row.get('amount_involved', 0)
            official_count = row.get('official_count', 0)
            
            # High risk criteria
            if amount > 10000000 or official_count > 5:  # >1 crore or >5 officials
                return 'CRITICAL'
            elif amount > 1000000 or official_count > 2:  # >10 lakh or >2 officials
                return 'HIGH'
            elif amount > 100000:  # >1 lakh
                return 'MEDIUM'
            else:
                return 'LOW'
        
        df['risk_level'] = df.apply(get_risk_level, axis=1)
        return df
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate data quality score"""
        def calculate_score(row) -> float:
            score = 1.0
            
            # Deduct for missing critical data
            if pd.isna(row.get('case_id')):
                score -= 0.3
            if pd.isna(row.get('institution_name')):
                score -= 0.3
            if pd.isna(row.get('amount_involved')) or row.get('amount_involved') == 0:
                score -= 0.2
            if pd.isna(row.get('date_reported')):
                score -= 0.2
            
            return max(0.0, score)
        
        df['data_quality_score'] = df.apply(calculate_score, axis=1)
        return df
    
    def _update_stats(self, df: pd.DataFrame):
        """Update extraction statistics"""
        self.stats['total_cases'] = len(df)
        self.stats['high_value_cases'] = len(df[df['amount_involved'] > 1000000])
        self.stats['cases_by_type'] = df['case_type'].value_counts().to_dict()
        self.stats['cases_by_institution'] = df['institution_type'].value_counts().to_dict()
    
    def get_stats(self) -> Dict:
        """Get extraction statistics"""
        return self.stats


if __name__ == "__main__":
    logger.info("Education Ministry Extractor Initialized")
    logger.info("Tracks: Scholarship Fraud, Fake Degrees, Exam Malpractices, Fund Misappropriation")
    logger.info("Detects: Education scams, teacher recruitment fraud, infrastructure corruption")
