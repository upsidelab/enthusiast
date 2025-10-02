import { useContext } from 'react';
import { ApplicationContext } from './application-context';

export const useSupportedFileExtensions = () => {
  const context = useContext(ApplicationContext);
  
  if (!context) {
    throw new Error('useSupportedFileExtensions must be used within an ApplicationContextProvider');
  }

  return {
    supportedExtensions: context.supportedFileExtensions,
    isLoading: context.isLoadingFileExtensions,
    error: context.fileExtensionsError,
  };
};
