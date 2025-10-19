import os
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
import requests
import pandas as pd

from constants import SUPPLEMENTED_STATIC_GTFS_URL


class GTFSLoader:
    """
    A class for downloading and managing GTFS data from URLs.

    This class handles downloading zip files from URLs, extracting them to a
    specified directory, and loading CSV files as pandas DataFrames.
    """

    def __init__(self, save_directory: str = "gtfs_data", verbose: bool = True):
        """
        Initialize the GTFSLoader with a save directory.

        Args:
            save_directory: Directory where GTFS files will be saved and extracted
            verbose: Whether to print progress messages (default: True)
        """
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

    def _log(self, message: str, end: str = "\n", flush: bool = False):
        """
        Print a message if verbose mode is enabled.

        Args:
            message: The message to print
            end: String appended after the message (default: newline)
            flush: Whether to forcibly flush the stream
        """
        if self.verbose:
            print(message, end=end, flush=flush)

    def fetch_and_extract_zip(
        self, url: str, timeout: int = 30, skip_if_exists: bool = False
    ) -> bool:
        """
        Fetch a zip file from a URL and extract it to the save directory.

        Args:
            url: The URL of the zip file to download
            timeout: Request timeout in seconds (default: 30)
            skip_if_exists: If True, skip download if save directory exists and contains files (default: False)

        Returns:
            bool: True if successful, False otherwise

        Raises:
            requests.RequestException: If there's an error downloading the file
            zipfile.BadZipFile: If the downloaded file is not a valid zip file
            OSError: If there's an error creating directories or extracting files
        """
        # Check if we should skip download
        if skip_if_exists and self.has_data():
            existing_files = self.list_available_files()
            self._log(
                f"Skipping download - directory '{self.save_directory}' already exists with {len(existing_files)} files"
            )
            return True
        # Create a temporary file to store the downloaded zip
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            try:
                self._log(f"Downloading zip file from: {url}")

                # Download the zip file
                response = requests.get(url, timeout=timeout, stream=True)
                response.raise_for_status()  # Raise an exception for bad status codes

                # Write the content to the temporary file
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)

                        # Simple progress indicator
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                        self._log(
                            f"\rDownload progress: {progress:.1f}%",
                            end="",
                            flush=True,
                        )

                self._log(f"\nDownload completed. File size: {downloaded_size} bytes")
                temp_file_path = temp_file.name

            except requests.RequestException as e:
                self._log(f"Error downloading file: {e}")
                return False

        try:
            # Extract the zip file
            self._log(f"Extracting zip file to: {self.save_directory}")

            with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
                # Get list of files in the zip
                file_list = zip_ref.namelist()
                self._log(f"Extracting {len(file_list)} files...")

                # Extract all files
                zip_ref.extractall(self.save_directory)

            self._log("Extraction completed successfully")
            return True

        except zipfile.BadZipFile as e:
            self._log(f"Error: Downloaded file is not a valid zip file: {e}")
            return False
        except OSError as e:
            self._log(f"Error extracting files: {e}")
            return False
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore errors when cleaning up temp file

    def fetch_static_supplemented_gtfs_data(self, skip_if_exists: bool = False) -> bool:
        """
        Convenience method to fetch supplemented static GTFS data.

        Args:
            skip_if_exists: If True, skip download if save directory exists and contains files (default: False)

        Returns:
            bool: True if successful, False otherwise
        """
        return self.fetch_and_extract_zip(
            SUPPLEMENTED_STATIC_GTFS_URL, skip_if_exists=skip_if_exists
        )

    def load_csv_as_dataframe(self, filename: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        Load a CSV file from the save directory as a pandas DataFrame.

        Args:
            filename: Name of the CSV file to load (e.g., "stops.txt", "routes.txt")
            **kwargs: Additional arguments to pass to pandas.read_csv()

        Returns:
            pandas.DataFrame if successful, None if file not found or error occurred

        Example:
            loader = GTFSLoader("gtfs_data")
            stops_df = loader.load_csv_as_dataframe("stops.txt")
            routes_df = loader.load_csv_as_dataframe("routes.txt", dtype={'route_id': str})
        """
        file_path = self.save_directory / filename

        if not file_path.exists():
            self._log(f"Error: File '{filename}' not found in {self.save_directory}")
            return None

        try:
            self._log(f"Loading {filename} as DataFrame...")
            df = pd.read_csv(file_path, **kwargs)
            self._log(f"Successfully loaded {len(df)} rows from {filename}")
            return df

        except Exception as e:
            self._log(f"Error loading {filename}: {e}")
            return None

    def list_available_files(self) -> list[str]:
        """
        List all files available in the save directory.

        Returns:
            List of filenames in the save directory
        """
        if not self.save_directory.exists():
            return []

        return [f.name for f in self.save_directory.iterdir() if f.is_file()]

    def get_file_path(self, filename: str) -> Path:
        """
        Get the full path to a file in the save directory.

        Args:
            filename: Name of the file

        Returns:
            Path object for the file
        """
        return self.save_directory / filename

    def has_data(self) -> bool:
        """
        Check if the save directory exists and contains files.

        Returns:
            bool: True if directory exists and has files, False otherwise
        """
        return self.save_directory.exists() and len(self.list_available_files()) > 0
