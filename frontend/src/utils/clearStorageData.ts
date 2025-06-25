/**
 * Utility to clear cached device data from browser storage
 * This helps resolve issues with stale or invalid device data
 */

export const clearDeviceStorageData = (): void => {
  try {
    // Clear localStorage entries related to devices
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (
        key.includes('device') || 
        key.includes('gps') ||
        key.includes('8781752668787835000') // Specific problematic IMEI
      )) {
        keysToRemove.push(key);
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
    // Clear sessionStorage entries related to devices  
    const sessionKeysToRemove = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key && (
        key.includes('device') || 
        key.includes('gps') ||
        key.includes('8781752668787835000') // Specific problematic IMEI
      )) {
        sessionKeysToRemove.push(key);
      }
    }
    
    sessionKeysToRemove.forEach(key => sessionStorage.removeItem(key));
    
    console.log('Device storage data cleared successfully');
  } catch (error) {
    console.error('Error clearing device storage data:', error);
  }
};

export const clearAllStorageData = (): void => {
  try {
    localStorage.clear();
    sessionStorage.clear();
    console.log('All storage data cleared successfully');
  } catch (error) {
    console.error('Error clearing all storage data:', error);
  }
};

export const logStorageContents = (): void => {
  console.log('=== localStorage contents ===');
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key) {
      console.log(`${key}: ${localStorage.getItem(key)}`);
    }
  }
  
  console.log('=== sessionStorage contents ===');
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    if (key) {
      console.log(`${key}: ${sessionStorage.getItem(key)}`);
    }
  }
}; 