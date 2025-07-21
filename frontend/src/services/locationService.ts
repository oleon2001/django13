// Type declarations for Google Maps (simplified)
declare global {
  interface Window {
    google?: {
      maps: {
        places: {
          AutocompleteService: new () => google.maps.places.AutocompleteService;
          PlacesService: new (div: HTMLElement) => google.maps.places.PlacesService;
          AutocompleteSessionToken: new () => google.maps.places.AutocompleteSessionToken;
          PlacesServiceStatus: {
            OK: string;
          };
        };
        Geocoder: new () => google.maps.Geocoder;
        GeocoderStatus: {
          OK: string;
        };
      };
    };
  }
}

// Simplified type definitions
namespace google.maps.places {
  export interface AutocompleteService {
    getPlacePredictions(
      request: any,
      callback: (predictions: any[] | null, status: string) => void
    ): void;
  }

  export interface PlacesService {
    getDetails(
      request: any,
      callback: (place: any | null, status: string) => void
    ): void;
  }

  export interface AutocompleteSessionToken {}
}

namespace google.maps {
  export interface Geocoder {
    geocode(
      request: any,
      callback: (results: any[] | null, status: string) => void
    ): void;
  }
}

interface LocationSuggestion {
  place_id: string;
  description: string;
  structured_formatting: {
    main_text: string;
    secondary_text: string;
  };
}

interface PlaceDetails {
  place_id: string;
  formatted_address: string;
  geometry: {
    location: {
      lat: number;
      lng: number;
    };
  };
  name?: string;
}

class LocationService {
  private autocompleteService: google.maps.places.AutocompleteService | null = null;
  private placesService: google.maps.places.PlacesService | null = null;
  private sessionToken: google.maps.places.AutocompleteSessionToken | null = null;

  constructor() {
    this.initializeGoogleMaps();
  }

  private async initializeGoogleMaps() {
    // Check if Google Maps is already loaded
    if (typeof window.google !== 'undefined' && window.google.maps && window.google.maps.places) {
      this.autocompleteService = new window.google.maps.places.AutocompleteService();
      // Create a hidden div for PlacesService
      const hiddenDiv = document.createElement('div');
      hiddenDiv.style.display = 'none';
      document.body.appendChild(hiddenDiv);
      this.placesService = new window.google.maps.places.PlacesService(hiddenDiv);
      return;
    }

    // Load Google Maps if not already loaded
    await this.loadGoogleMapsScript();
  }

  private loadGoogleMapsScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Check if script is already loading or loaded
      if (document.querySelector('script[src*="maps.googleapis.com"]')) {
        // Wait for Google to be available
        const checkGoogle = () => {
          if (typeof window.google !== 'undefined' && window.google.maps && window.google.maps.places) {
            this.autocompleteService = new window.google.maps.places.AutocompleteService();
            const hiddenDiv = document.createElement('div');
            hiddenDiv.style.display = 'none';
            document.body.appendChild(hiddenDiv);
            this.placesService = new window.google.maps.places.PlacesService(hiddenDiv);
            resolve();
          } else {
            setTimeout(checkGoogle, 100);
          }
        };
        checkGoogle();
        return;
      }

      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&libraries=places&language=es`;
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        this.autocompleteService = new window.google!.maps.places.AutocompleteService();
        const hiddenDiv = document.createElement('div');
        hiddenDiv.style.display = 'none';
        document.body.appendChild(hiddenDiv);
        this.placesService = new window.google!.maps.places.PlacesService(hiddenDiv);
        resolve();
      };
      
      script.onerror = () => {
        reject(new Error('Failed to load Google Maps script'));
      };
      
      document.head.appendChild(script);
    });
  }

  /**
   * Search for location suggestions based on input
   */
  async searchLocations(input: string): Promise<LocationSuggestion[]> {
    if (!this.autocompleteService) {
      // Fallback to mock data if Google Maps is not available
      return this.getMockSuggestions(input);
    }

    if (!input || input.length < 3) {
      return [];
    }

    return new Promise((resolve) => {
      // Create a new session token for this search session
      if (!this.sessionToken) {
        this.sessionToken = new window.google!.maps.places.AutocompleteSessionToken();
      }

      this.autocompleteService!.getPlacePredictions(
        {
          input,
          sessionToken: this.sessionToken,
          componentRestrictions: { country: ['mx'] }, // Restrict to Mexico
          types: ['establishment', 'geocode'], // Include businesses and addresses
        },
        (predictions, status) => {
          if (status === window.google!.maps.places.PlacesServiceStatus.OK && predictions) {
            const suggestions: LocationSuggestion[] = predictions.map((prediction: any) => ({
              place_id: prediction.place_id,
              description: prediction.description,
              structured_formatting: {
                main_text: prediction.structured_formatting?.main_text || prediction.description,
                secondary_text: prediction.structured_formatting?.secondary_text || '',
              },
            }));
            resolve(suggestions);
          } else {
            // Fallback to mock data on error
            resolve(this.getMockSuggestions(input));
          }
        }
      );
    });
  }

  /**
   * Get detailed information about a place
   */
  async getPlaceDetails(placeId: string): Promise<PlaceDetails | null> {
    if (!this.placesService) {
      // Fallback coordinates for common Mexican cities
      const mockDetails = this.getMockPlaceDetails(placeId);
      return mockDetails;
    }

    return new Promise((resolve) => {
      this.placesService!.getDetails(
        {
          placeId,
          fields: ['place_id', 'formatted_address', 'geometry', 'name'],
          sessionToken: this.sessionToken!,
        },
        (place: any, status: string) => {
          // Clear session token after use
          this.sessionToken = null;

          if (status === window.google!.maps.places.PlacesServiceStatus.OK && place) {
            const details: PlaceDetails = {
              place_id: place.place_id!,
              formatted_address: place.formatted_address!,
              geometry: {
                location: {
                  lat: place.geometry!.location!.lat(),
                  lng: place.geometry!.location!.lng(),
                },
              },
              name: place.name,
            };
            resolve(details);
          } else {
            // Fallback to mock data
            resolve(this.getMockPlaceDetails(placeId));
          }
        }
      );
    });
  }

  /**
   * Get current user location
   */
  async getCurrentLocation(): Promise<{ lat: number; lng: number } | null> {
    if (!navigator.geolocation) {
      return null;
    }

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        () => {
          resolve(null);
        }
      );
    });
  }

  /**
   * Reverse geocode coordinates to get address
   */
  async reverseGeocode(lat: number, lng: number): Promise<string> {
    if (!window.google?.maps) {
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }

    return new Promise((resolve) => {
      const geocoder = new window.google!.maps.Geocoder();
      geocoder.geocode(
        { location: { lat, lng } },
        (results: any[] | null, status: string) => {
          if (status === window.google!.maps.GeocoderStatus.OK && results && results[0]) {
            resolve(results[0].formatted_address);
          } else {
            resolve(`${lat.toFixed(6)}, ${lng.toFixed(6)}`);
          }
        }
      );
    });
  }

  /**
   * Mock suggestions for when Google Maps is not available
   */
  private getMockSuggestions(input: string): LocationSuggestion[] {
    const mockData = [
      {
        place_id: 'mock_cdmx',
        description: `${input} - Ciudad de México, CDMX, México`,
        structured_formatting: {
          main_text: input,
          secondary_text: 'Ciudad de México, CDMX, México',
        },
      },
      {
        place_id: 'mock_guadalajara',
        description: `${input} - Guadalajara, Jalisco, México`,
        structured_formatting: {
          main_text: input,
          secondary_text: 'Guadalajara, Jalisco, México',
        },
      },
      {
        place_id: 'mock_monterrey',
        description: `${input} - Monterrey, Nuevo León, México`,
        structured_formatting: {
          main_text: input,
          secondary_text: 'Monterrey, Nuevo León, México',
        },
      },
      {
        place_id: 'mock_puebla',
        description: `${input} - Puebla, Puebla, México`,
        structured_formatting: {
          main_text: input,
          secondary_text: 'Puebla, Puebla, México',
        },
      },
      {
        place_id: 'mock_tijuana',
        description: `${input} - Tijuana, Baja California, México`,
        structured_formatting: {
          main_text: input,
          secondary_text: 'Tijuana, Baja California, México',
        },
      },
    ];

    return mockData.filter(item => 
      item.structured_formatting.main_text.toLowerCase().includes(input.toLowerCase()) ||
      item.structured_formatting.secondary_text.toLowerCase().includes(input.toLowerCase())
    );
  }

  /**
   * Mock place details for fallback
   */
  private getMockPlaceDetails(placeId: string): PlaceDetails | null {
    const mockCoordinates: Record<string, { lat: number; lng: number; address: string }> = {
      mock_cdmx: {
        lat: 19.4326,
        lng: -99.1332,
        address: 'Ciudad de México, CDMX, México',
      },
      mock_guadalajara: {
        lat: 20.6597,
        lng: -103.3496,
        address: 'Guadalajara, Jalisco, México',
      },
      mock_monterrey: {
        lat: 25.6866,
        lng: -100.3161,
        address: 'Monterrey, Nuevo León, México',
      },
      mock_puebla: {
        lat: 19.0414,
        lng: -98.2063,
        address: 'Puebla, Puebla, México',
      },
      mock_tijuana: {
        lat: 32.5149,
        lng: -117.0382,
        address: 'Tijuana, Baja California, México',
      },
    };

    const details = mockCoordinates[placeId];
    if (!details) return null;

    return {
      place_id: placeId,
      formatted_address: details.address,
      geometry: {
        location: {
          lat: details.lat,
          lng: details.lng,
        },
      },
    };
  }
}

// Export singleton instance
export const locationService = new LocationService();
export type { LocationSuggestion, PlaceDetails }; 