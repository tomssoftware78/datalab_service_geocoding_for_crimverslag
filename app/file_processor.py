import logging
import pandas as pd

from pathlib import Path
from config import OUTPUT_FOLDER, REPLACEMENTS, KEYWORDS, REFGEB_CODES
from geocoding_service import GeocodingService

class FileProcessor:

    geocoding_service: GeocodingService

    @property
    def logger(self):
        # Create a logger specific to this class
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def __init__(self):
        self.geocoding_service = GeocodingService()
    

    def process_file(self, input_path: Path):
        output_path = OUTPUT_FOLDER / input_path.with_stem(input_path.stem + "_processed").name
    
        # Try reading as Excel or HTML-misnamed Excel
        try:
            if input_path.suffix == '.xls':
                try:
                    df = pd.read_excel(input_path, engine='xlrd')
                except Exception:
                    df_list = pd.read_html(input_path)
                    df = df_list[0]
            else:
                df = pd.read_excel(input_path, engine='openpyxl')
        except Exception as e:
            raise ValueError(f"❌ Failed to read {input_path.name}: {e}")
    
        if df.empty:
            self.logger.debug(f"❌ DataFrame is empty: {input_path.name}")
        else:
            # Ensure required columns exist
            required_cols = ['Type', 'RefGeb', 'TxtCrim', 'TxtISLP', 'Land', 'Straat', 'Nummer']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"❌ Missing required columns in {input_path.name}: {missing_cols}")
        
            self.logger.debug("📄 Loaded %d rows from %s", len(df), input_path.name)
        
            # Fix encoding
            for col in df.select_dtypes(include='object').columns:
                df[col] = df[col].apply(self.fix_encoding)
        
            # Filters
            df = df[df['Type'] != 'IV']
            df = df[~df['RefGeb'].str.contains(r'navolgend', case=False, na=False)]
        
            if not df.empty:
                # Keywords
                df['Trefwoorden'] = df.apply(self.find_keywords, axis=1)
            
                # Expand RefGeb
                df['RefGebVoluit'] = df['RefGeb'].apply(self.expand_refgeb)
            
                # Reorder columns
                cols = df.columns.tolist()
                if 'RefGebVoluit' in cols:
                    cols.remove('RefGebVoluit')
                    insert_index = cols.index('RefGeb') + 1 if 'RefGeb' in cols else len(cols)
                    cols = cols[:insert_index] + ['RefGebVoluit'] + cols[insert_index:]
                df = df[cols]
            
                if 'Trefwoorden' in df.columns:
                    cols = df.columns.tolist()
                    cols.remove('Trefwoorden')
                    insert_index = cols.index('Land') + 1 if 'Land' in cols else len(cols)
                    cols = cols[:insert_index] + ['Trefwoorden'] + cols[insert_index:]
                    df = df[cols]
            
                df['Localisatie'] = df['Straat'].fillna('') + ' ' + df['Nummer'].fillna('').astype(str)
            
                # lon, lat en score vragen aan de geocoding service en toevoegen aan dataframe
                df[["lon", "lat", "score"]] = df.apply(lambda row: pd.Series(self.geocoding_service.get_x_y_from_geocoding_service(row)), axis=1)


        df.to_excel(output_path, index=False)
        self.logger.debug("✅ Saved processed file to: %s", output_path)
    
        input_path.unlink()
        self.logger.debug("🗑️  Deleted original file: %s", input_path)

    def fix_encoding(self, text):
        if isinstance(text, str):
            for wrong, correct in REPLACEMENTS.items():
                text = text.replace(wrong, correct)
        return text
    
    # Keywords
    def find_keywords(self, row):
        found = set()
        for col in ['TxtCrim', 'TxtISLP']:
            text = str(row[col]).lower() if pd.notna(row[col]) else ''
            for kw in KEYWORDS:
                if kw.lower() in text:
                    found.add(kw)
        return ", ".join(sorted(found)) if found else ""
    
    # Expand RefGeb
    def expand_refgeb(self, refgeb_value):
        if pd.isna(refgeb_value):
            return ""
        cleaned = refgeb_value.replace('aanvankelijk', '').strip()
        parts = [part.strip() for part in cleaned.split(';') if part.strip()]
        matches = [REFGEB_CODES[code] for code in parts if code in REFGEB_CODES]
        return ";".join(matches)
