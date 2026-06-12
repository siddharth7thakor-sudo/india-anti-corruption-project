  """
Welfare Fraud Connector - Dynamic Multi-Portal Data Integration
India Anti-Corruption Project 2.0

This module dynamically connects to multiple Indian government welfare scheme portals,
extracts data, and provides fraud detection capabilities across schemes.

Supported Portals:
- NSAP (National Social Assistance Programme)
- MGNREGA MIS
- PDS / e-PDS
- PM-KISAN
- Open Government Data Platform (data.gov.in)
- Union Budget Portal
- Jan Soochna Portal (Rajasthan)
- State Transparency Portals

Author: Siddharth Thakor-sudo
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WelfareSchemeType(Enum):
    PENSION = "pension"
    EMPLOYMENT = "employment"
    FOOD_SECURITY = "food_security"
    AGRICULTURE = "agriculture"
    SCHOLARSHIP = "scholarship"
    BUDGET = "budget"
    GENERAL = "general"


@dataclass
class DataSource:
    name: str
    url: str
    scheme_type: WelfareSchemeType
    data_type: str  # 'json', 'html', 'csv', 'api'
    requires_auth: bool = False
    is_active: bool = True
    last_updated: Optional[datetime] = None
    extracted_data: Optional[pd.DataFrame] = field(default=None, repr=False)
    

@dataclass
class FraudIndicator:
    indicator_name: str
    scheme_source: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    affected_entities: List[str]
    confidence_score: float
    timestamp: datetime


# =============================================================================
# 1. DATASOURCE REGISTRY
# =============================================================================

class DataSourceRegistry:
    """
    Central registry for all welfare scheme data sources.
    Dynamically manages connections and extracts data.
    """
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {
            # Core Data and Audit Portals
            "open_gov_data": DataSource(
                name="Open Government Data Platform",
                url="https://data.gov.in/",
                scheme_type=WelfareSchemeType.GENERAL,
                data_type="api",
                is_active=True
            ),
            "union_budget": DataSource(
                name="Union Budget Portal",
                url="https://www.indiabudget.gov.in/",
                scheme_type=WelfareSchemeType.BUDGET,
                data_type="html",
                is_active=True
            ),
            "mospi_projects": DataSource(
                name="MoSPI Project Monitoring",
                url="https://www.mospi.gov.in/",
                scheme_type=WelfareSchemeType.GENERAL,
                data_type="html",
                is_active=True
            ),
            "cag_reports": DataSource(
                name="CAG Audit Reports",
                url="https://cag.gov.in/",
                scheme_type=WelfareSchemeType.GENERAL,
                data_type="html",
                is_active=True
            ),
            # Welfare Scheme MIS
            "nsap": DataSource(
                name="NSAP - National Social Assistance Programme",
                url="https://nsap.dord.gov.in/",
                scheme_type=WelfareSchemeType.PENSION,
                data_type="html",
                is_active=True
            ),
            "mgnrega": DataSource(
                name="MGNREGA MIS",
                url="https://nreganarep.nic.in/",
                scheme_type=WelfareSchemeType.EMPLOYMENT,
                data_type="html",
                is_active=True
            ),
            "pds": DataSource(
                name="PDS / e-PDS Portal",
                url="https://pdsportal.gov.in/",
                scheme_type=WelfareSchemeType.FOOD_SECURITY,
                data_type="html",
                is_active=True
            ),
            "pmkisan": DataSource(
                name="PM-KISAN Portal",
                url="https://pmkisan.gov.in/",
                scheme_type=WelfareSchemeType.AGRICULTURE,
                data_type="html",
                is_active=True
            ),
            "jan_soochna": DataSource(
                name="Jan Soochna Portal (Rajasthan)",
                url="https://jansoochna.rajasthan.gov.in/Scheme",
                scheme_type=WelfareSchemeType.GENERAL,
                data_type="html",
                is_active=True
            ),
            "social_justice": DataSource(
                name="Social Justice Schemes",
                url="https://socialjustice.gov.in/schemes",
                scheme_type=WelfareSchemeType.SCHOLARSHIP,
                data_type="html",
                is_active=True
            )
        }
    
    def get_source(self, name: str) -> Optional[DataSource]:
        return self.sources.get(name)
    
    def get_active_sources(self) -> List[DataSource]:
        return [s for s in self.sources.values() if s.is_active]
    
    def get_sources_by_type(self, scheme_type: WelfareSchemeType) -> List[DataSource]:
        return [s for s in self.sources.values() if s.scheme_type == scheme_type and s.is_active]
    
    def add_source(self, name: str, source: DataSource) -> None:
        self.sources[name] = source
        logger.info(f"Added new data source: {source.name}")
    
    def toggle_source(self, name: str, active: bool) -> None:
        if name in self.sources:
            self.sources[name].is_active = active
            status = "activated" if active else "deactivated"
            logger.info(f"Data source {name} {status}")


# =============================================================================
# 2. BASE DATA CONNECTOR
# =============================================================================

class BaseConnector:
    """Base class for all data connectors."""
    
    def __init__(self, source: DataSource):
        self.source = source
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def connect(self) -> bool:
        """Test connection to the data source."""
        try:
            response = self.session.get(self.source.url, timeout=10)
            return response.status_code in [200, 206]
        except Exception as e:
            logger.error(f"Connection failed for {self.source.name}: {e}")
            return False
    
    def fetch_data(self, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """Override in subclasses."""
        raise NotImplementedError

# =============================================================================
# 3. SCHEME-SPECIFIC CONNECTORS
# =============================================================================

class NSAPConnector(BaseConnector):
    """Connector for National Social Assistance Programme."""
    
    def fetch_pension_beneficiaries(self, state: str = None, category: str = None) -> pd.DataFrame:
        """Fetch pension beneficiary data with ghost detection."""
        logger.info(f"Fetching NSAP data - State: {state}, Category: {category}")
        # Simulated data structure - replace with actual API/scraper
        data = {
            'beneficiary_id': ['NSAP001', 'NSAP002', 'NSAP003'],
            'name': ['Beneficiary A', 'Beneficiary B', 'Beneficiary C'],
            'state': [state or 'MAH', state or 'UP', state or 'RJ'],
            'category': [category or 'OLD_AGE', category or 'WIDOW', category or 'DISABLED'],
            'amount': [1500, 1000, 1200],
            'status': ['active', 'inactive', 'active'],
            'last_payment': ['2026-05-01', '2026-03-15', '2026-06-01']
        }
        return pd.DataFrame(data)
    
    def detect_ghost_beneficiaries(self, df: pd.DataFrame) -> List[str]:
        return list(df[df['status'] == 'inactive']['beneficiary_id'])


class MGNREGAConnector(BaseConnector):
    """Connector for MGNREGA MIS data."""
    
    def fetch_worker_muster(self, district: str, panchayat: str = None) -> pd.DataFrame:
        """Fetch worker and muster roll data."""
        logger.info(f"Fetching MGNREGA data - District: {district}")
        data = {
            'worker_id': ['MG001', 'MG002', 'MG003'],
            'name': ['Worker X', 'Worker Y', 'Worker Z'],
            'district': [district, district, district],
            'days_worked': [100, 120, 45],
            'wage_paid': [25000, 30000, 11250],
            'block_allotment': [district + '_BLK1', district + '_BLK1', district + '_BLK2'],
            'work_type': ['road', 'irrigation', 'soil_conservation']
        }
        return pd.DataFrame(data)
    
    def detect_ghost_workers(self, df: pd.DataFrame, max_days: int = 100) -> pd.DataFrame:
        return df[df['days_worked'] > max_days]
    
    def detect_anomalous_wages(self, df: pd.DataFrame) -> pd.DataFrame:
        avg_wage_per_day = df['wage_paid'] / df['days_worked']
        threshold = avg_wage_per_day.mean() * 1.5
        return df[avg_wage_per_day > threshold]


class PDSConnector(BaseConnector):
    """Connector for PDS / e-PDS data."""
    
    def fetch_ration_cards(self, state: str, shop_id: str = None) -> pd.DataFrame:
        data = {
            'card_number': ['RC001', 'RC002', 'RC003', 'RC004'],
            'household_head': ['HH1', 'HH2', 'HH3', 'HH2'],  # duplicate household
            'state': [state, state, state, state],
            'shop_id': [shop_id or 'S001', shop_id or 'S001', 'S002', shop_id or 'S001'],
            'rice_allocated': [35, 30, 25, 30],
            'rice_lifted': [35, 30, 0, 30],
            'wheat_allocated': [20, 15, 10, 15],
            'wheat_lifted': [20, 15, 0, 15],
            'card_type': ['BPL', 'APL', 'AAY', 'BPL']
        }
        return pd.DataFrame(data)
    
    def detect_ghost_cards(self, df: pd.DataFrame) -> pd.DataFrame:
        # Cards with zero lifting are suspicious
        return df[(df['rice_lifted'] == 0) & (df['wheat_lifted'] == 0)]
    
    def detect_leakage(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df['rice_lifted'] > df['rice_allocated']]


class PMKISANConnector(BaseConnector):
    """Connector for PM-KISAN beneficiary data."""
    
    def fetch_beneficiary_status(self, name: str, aadhaar: str = None) -> Dict:
        data = {
            'beneficiary_id': 'PMK001',
            'name': name,
            'aadhaar_last4': aadhaar[-4:] if aadhaar else 'XXXX',
            'state': 'MAH',
            'district': 'PUNE',
            'instalments': [6000, 6000, 6000, 6000, 6000, 6000],
            'status': 'active',
            'land_area_acres': 2.5
        }
        return data
    
    def detect_duplicate_payments(self, beneficiaries: List[Dict]) -> List[str]:
        ids = [b['beneficiary_id'] for b in beneficiaries]
        seen = set()
        duplicates = []
        for id_ in ids:
            if id_ in seen:
                duplicates.append(id_)
            seen.add(id_)
        return duplicates


class JanSoochnaConnector(BaseConnector):
    """Connector for Jan Soochna Portal (Rajasthan)."""
    
    def fetch_scheme_data(self, scheme_name: str, district: str) -> pd.DataFrame:
        data = {
            'scheme': [scheme_name, scheme_name, scheme_name],
            'district': [district, district, district],
            'beneficiary_id': ['JS001', 'JS002', 'JS003'],
            'amount_disbursed': [5000, 3000, 8000],
            'status': ['completed', 'pending', 'completed'],
            'date': ['2026-04-01', '2026-05-01', '2026-03-01']
        }
        return pd.DataFrame(data)


# =============================================================================
# 4. FRAUD DETECTION ENGINE
# =============================================================================

class FraudDetectionEngine:
    """
    Central fraud detection engine that aggregates indicators
    from multiple welfare scheme data sources.
    """
    
    def __init__(self, registry: DataSourceRegistry):
        self.registry = registry
        self.indicators: List[FraudIndicator] = []
        self.connectors: Dict[str, BaseConnector] = {}
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        for name, source in self.registry.sources.items():
            if not source.is_active:
                continue
            connector = None
            if name == 'nsap':
                connector = NSAPConnector(source)
            elif name == 'mgnrega':
                connector = MGNREGAConnector(source)
            elif name == 'pds':
                connector = PDSConnector(source)
            elif name == 'pmkisan':
                connector = PMKISANConnector(source)
            elif name == 'jan_soochna':
                connector = JanSoochnaConnector(source)
            else:
                connector = BaseConnector(source)
            self.connectors[name] = connector
    
    def run_all_checks(self) -> List[FraudIndicator]:
        """Run all fraud detection checks across all sources."""
        self.indicators = []
        
        # NSAP ghost beneficiaries
        if 'nsap' in self.connectors:
            df = self.connectors['nsap'].fetch_pension_beneficiaries()
            ghosts = self.connectors['nsap'].detect_ghost_beneficiaries(df)
            if ghosts:
                self.indicators.append(FraudIndicator(
                    indicator_name="NSAP_GHOST_BENEFICIARY",
                    scheme_source="NSAP",
                    severity="high",
                    description=f"Found {len(ghosts)} inactive ghost beneficiaries still in system",
                    affected_entities=ghosts,
                    confidence_score=0.85,
                    timestamp=datetime.now()
                ))
        
        # MGNREGA ghost workers
        if 'mgnrega' in self.connectors:
            df = self.connectors['mgnrega'].fetch_worker_muster('JAIPUR')
            wage_anomalies = self.connectors['mgnrega'].detect_anomalous_wages(df)
            if not wage_anomalies.empty:
                self.indicators.append(FraudIndicator(
                    indicator_name="MGNREGA_WAGE_ANOMALY",
                    scheme_source="MGNREGA",
                    severity="medium",
                    description=f"Found {len(wage_anomalies)} workers with anomalous wage patterns",
                    affected_entities=list(wage_anomalies['worker_id']),
                    confidence_score=0.70,
                    timestamp=datetime.now()
                ))
        
        # PDS ghost cards and leakage
        if 'pds' in self.connectors:
            df = self.connectors['pds'].fetch_ration_cards('RJ')
            ghost_cards = self.connectors['pds'].detect_ghost_cards(df)
            if not ghost_cards.empty:
                self.indicators.append(FraudIndicator(
                    indicator_name="PDS_GHOST_CARD",
                    scheme_source="PDS",
                    severity="critical",
                    description=f"Found {len(ghost_cards)} ghost ration cards with zero lifting",
                    affected_entities=list(ghost_cards['card_number']),
                    confidence_score=0.90,
                    timestamp=datetime.now()
                ))
        
        # Cross-scheme duplicate check
        self._check_cross_scheme_duplicates()
        
        return self.indicators
    
    def _check_cross_scheme_duplicates(self):
        """Detect same entity claiming benefits across multiple schemes."""
        logger.info("Running cross-scheme duplicate detection...")
        # Placeholder for cross-scheme logic
        pass
    
    def generate_report(self) -> str:
        """Generate a summary fraud report."""
        report = f"""\n{'='*60}
WELFARE FRAUD DETECTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for ind in self.indicators:
            severity_counts[ind.severity] = severity_counts.get(ind.severity, 0) + 1
            report += f"\n[{ind.severity.upper()}] {ind.indicator_name}"
            report += f"\n  Source: {ind.scheme_source}"
            report += f"\n  Description: {ind.description}"
            report += f"\n  Confidence: {ind.confidence_score:.2f}"
            report += f"\n  Affected Entities: {', '.join(ind.affected_entities) if ind.affected_entities else 'N/A'}"
        
        report += f"\n
{'='*60}
SUMMARY"
        report += f"\nTotal Indicators: {len(self.indicators)}"
        report += f"\n  Critical: {severity_counts.get('critical', 0)}"
        report += f"\n  High: {severity_counts.get('high', 0)}"
        report += f"\n  Medium: {severity_counts.get('medium', 0)}"
        report += f"\n  Low: {severity_counts.get('low', 0)}"
        report += f"\n{'='*60}"
        
        return report


# =============================================================================
# 5. MAIN INTERFACE
# =============================================================================

class WelfareFraudConnector:
    """
    Main entry point for the Welfare Fraud Connector.
    Provides a unified interface for all fraud detection operations.
    """
    
    def __init__(self):
        self.registry = DataSourceRegistry()
        self.engine = FraudDetectionEngine(self.registry)
    
    def connect_all(self) -> Dict[str, bool]:
        """Test connections to all active data sources."""
        results = {}
        for name, connector in self.engine.connectors.items():
            results[name] = connector.connect()
        return results
    
    def scan(self) -> List[FraudIndicator]:
        """Run comprehensive fraud scan across all sources."""
        return self.engine.run_all_checks()
    
    def report(self) -> str:
        """Generate and return a fraud detection report."""
        self.scan()
        return self.engine.generate_report()
    
    def add_custom_source(self, name: str, url: str, 
                         scheme_type: WelfareSchemeType) -> None:
        """Register a new custom data source."""
        source = DataSource(
            name=name,
            url=url,
            scheme_type=scheme_type,
            data_type='api'
        )
        self.registry.add_source(name, source)


# =============================================================================
# DEMO / USAGE
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    
    # Initialize the connector
    connector = WelfareFraudConnector()
    
    # Test connections
    print("Testing data source connections...")
    status = connector.connect_all()
    for source, connected in status.items():
        print(f"  {source}: {'CONNECTED' if connected else 'FAILED'}")
    
    # Run fraud detection
    print("\nRunning fraud detection scan...")
    indicators = connector.scan()
    
    # Print report
    print(connector.report())
    
    # Demo: Add custom data source
    print("\nRegistering custom data source...")
    connector.add_custom_source(
        name="custom_state_portal",
        url="https://example-state.gov.in/transparency",
        scheme_type=WelfareSchemeType.GENERAL
    )
    print(f"Active sources: {[s.name for s in connector.registry.get_active_sources()]}")
