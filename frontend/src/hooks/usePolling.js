import { useEffect, useRef } from 'react';

/**
 * Custom hook to execute a callback function at regular intervals.
 * Automatically stops polling if the component unmounts or if active becomes false.
 * 
 * @param {Function} callback Function to execute
 * @param {number} delay Delay in milliseconds
 * @param {boolean} active Whether polling is active
 */
export function usePolling(callback, delay, active = true) {
  const savedCallback = useRef(callback);

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    if (!active || delay === null || delay === undefined) {
      return;
    }

    const id = setInterval(() => {
      savedCallback.current();
    }, delay);

    return () => clearInterval(id);
  }, [delay, active]);
}
