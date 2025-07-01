import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { AxiosError, AxiosResponse } from 'axios';
import { toast } from 'react-toastify';
import { ApiResponse, PaginationParams } from '../types/unified';

// ============================================================================
// TYPES - Tipos para el hook de API
// ============================================================================

export interface QueryConfig<T> extends Omit<UseQueryOptions<T, AxiosError>, 'queryKey' | 'queryFn'> {
  showErrorToast?: boolean;
  showSuccessToast?: boolean;
  errorMessage?: string;
  successMessage?: string;
}

export interface MutationConfig<TData, TVariables> extends Omit<UseMutationOptions<TData, AxiosError, TVariables>, 'mutationFn'> {
  showErrorToast?: boolean;
  showSuccessToast?: boolean;
  errorMessage?: string;
  successMessage?: string;
  invalidateQueries?: string[];
}

// ============================================================================
// UTILITY FUNCTIONS - Funciones de utilidad
// ============================================================================

const handleApiError = (error: AxiosError, customMessage?: string) => {
  const message = customMessage || error.response?.data?.message || error.message || 'An error occurred';
  console.error('API Error:', error);
  return message;
};

const handleApiSuccess = (message?: string) => {
  if (message) {
    toast.success(message);
  }
};

// ============================================================================
// CUSTOM HOOKS - Hooks personalizados
// ============================================================================

/**
 * Hook personalizado para consultas GET con React Query
 */
export function useApiQuery<T>(
  queryKey: string[],
  queryFn: () => Promise<AxiosResponse<ApiResponse<T>>>,
  config: QueryConfig<T> = {}
) {
  const {
    showErrorToast = true,
    errorMessage,
    ...queryConfig
  } = config;

  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const response = await queryFn();
        return response.data.data || response.data;
      } catch (error) {
        const message = handleApiError(error as AxiosError, errorMessage);
        if (showErrorToast) {
          toast.error(message);
        }
        throw error;
      }
    },
    ...queryConfig,
  });
}

/**
 * Hook personalizado para consultas GET con paginación
 */
export function useApiQueryPaginated<T>(
  queryKey: string[],
  queryFn: (params: PaginationParams) => Promise<AxiosResponse<ApiResponse<T[]>>>,
  params: PaginationParams = {},
  config: QueryConfig<T[]> = {}
) {
  const {
    showErrorToast = true,
    errorMessage,
    ...queryConfig
  } = config;

  return useQuery({
    queryKey: [...queryKey, params],
    queryFn: async () => {
      try {
        const response = await queryFn(params);
        return {
          data: response.data.data || response.data,
          pagination: response.data.pagination,
        };
      } catch (error) {
        const message = handleApiError(error as AxiosError, errorMessage);
        if (showErrorToast) {
          toast.error(message);
        }
        throw error;
      }
    },
    ...queryConfig,
  });
}

/**
 * Hook personalizado para mutaciones POST/PUT/PATCH/DELETE
 */
export function useApiMutation<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<AxiosResponse<ApiResponse<TData>>>,
  config: MutationConfig<TData, TVariables> = {}
) {
  const queryClient = useQueryClient();
  const {
    showErrorToast = true,
    showSuccessToast = true,
    errorMessage,
    successMessage,
    invalidateQueries = [],
    ...mutationConfig
  } = config;

  return useMutation({
    mutationFn: async (variables: TVariables) => {
      try {
        const response = await mutationFn(variables);
        const data = response.data.data || response.data;
        
        if (showSuccessToast && successMessage) {
          handleApiSuccess(successMessage);
        }
        
        // Invalidar queries especificadas
        if (invalidateQueries.length > 0) {
          invalidateQueries.forEach(queryKey => {
            queryClient.invalidateQueries({ queryKey: [queryKey] });
          });
        }
        
        return data;
      } catch (error) {
        const message = handleApiError(error as AxiosError, errorMessage);
        if (showErrorToast) {
          toast.error(message);
        }
        throw error;
      }
    },
    ...mutationConfig,
  });
}

/**
 * Hook personalizado para mutaciones con optimistic updates
 */
export function useApiMutationOptimistic<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<AxiosResponse<ApiResponse<TData>>>,
  queryKey: string[],
  updateFn: (oldData: TData[], newItem: TData) => TData[],
  config: MutationConfig<TData, TVariables> = {}
) {
  const queryClient = useQueryClient();
  const {
    showErrorToast = true,
    showSuccessToast = true,
    errorMessage,
    successMessage,
    ...mutationConfig
  } = config;

  return useMutation({
    mutationFn: async (variables: TVariables) => {
      try {
        const response = await mutationFn(variables);
        const data = response.data.data || response.data;
        
        if (showSuccessToast && successMessage) {
          handleApiSuccess(successMessage);
        }
        
        return data;
      } catch (error) {
        const message = handleApiError(error as AxiosError, errorMessage);
        if (showErrorToast) {
          toast.error(message);
        }
        throw error;
      }
    },
    onMutate: async (newItem) => {
      // Cancelar queries en curso
      await queryClient.cancelQueries({ queryKey });
      
      // Snapshot del valor anterior
      const previousData = queryClient.getQueryData<TData[]>(queryKey);
      
      // Optimistic update
      queryClient.setQueryData<TData[]>(queryKey, (old) => {
        return old ? updateFn(old, newItem as TData) : [newItem as TData];
      });
      
      return { previousData };
    },
    onError: (err, newItem, context) => {
      // Revertir en caso de error
      if (context?.previousData) {
        queryClient.setQueryData(queryKey, context.previousData);
      }
    },
    onSettled: () => {
      // Refetch para asegurar sincronización
      queryClient.invalidateQueries({ queryKey });
    },
    ...mutationConfig,
  });
}

/**
 * Hook personalizado para operaciones CRUD
 */
export function useCrudOperations<T>(
  baseQueryKey: string,
  api: {
    getAll: (params?: PaginationParams) => Promise<AxiosResponse<ApiResponse<T[]>>>;
    getById: (id: number) => Promise<AxiosResponse<ApiResponse<T>>>;
    create: (data: Partial<T>) => Promise<AxiosResponse<ApiResponse<T>>>;
    update: (id: number, data: Partial<T>) => Promise<AxiosResponse<ApiResponse<T>>>;
    delete: (id: number) => Promise<AxiosResponse<ApiResponse<boolean>>>;
  }
) {
  const queryClient = useQueryClient();

  // Query para obtener todos los elementos
  const useGetAll = (params: PaginationParams = {}, config: QueryConfig<T[]> = {}) => {
    return useApiQueryPaginated(
      [baseQueryKey, 'list'],
      () => api.getAll(params),
      params,
      config
    );
  };

  // Query para obtener un elemento por ID
  const useGetById = (id: number, config: QueryConfig<T> = {}) => {
    return useApiQuery(
      [baseQueryKey, 'detail', id.toString()],
      () => api.getById(id),
      config
    );
  };

  // Mutation para crear
  const useCreate = (config: MutationConfig<T, Partial<T>> = {}) => {
    return useApiMutation(
      (data: Partial<T>) => api.create(data),
      {
        invalidateQueries: [baseQueryKey],
        successMessage: 'Created successfully',
        errorMessage: 'Failed to create',
        ...config,
      }
    );
  };

  // Mutation para actualizar
  const useUpdate = (config: MutationConfig<T, { id: number; data: Partial<T> }> = {}) => {
    return useApiMutation(
      ({ id, data }: { id: number; data: Partial<T> }) => api.update(id, data),
      {
        invalidateQueries: [baseQueryKey],
        successMessage: 'Updated successfully',
        errorMessage: 'Failed to update',
        ...config,
      }
    );
  };

  // Mutation para eliminar
  const useDelete = (config: MutationConfig<boolean, number> = {}) => {
    return useApiMutation(
      (id: number) => api.delete(id),
      {
        invalidateQueries: [baseQueryKey],
        successMessage: 'Deleted successfully',
        errorMessage: 'Failed to delete',
        ...config,
      }
    );
  };

  // Función para invalidar cache
  const invalidateCache = () => {
    queryClient.invalidateQueries({ queryKey: [baseQueryKey] });
  };

  // Función para actualizar cache manualmente
  const updateCache = (updater: (oldData: T[] | undefined) => T[]) => {
    queryClient.setQueryData([baseQueryKey, 'list'], updater);
  };

  return {
    useGetAll,
    useGetById,
    useCreate,
    useUpdate,
    useDelete,
    invalidateCache,
    updateCache,
  };
}

/**
 * Hook personalizado para operaciones en tiempo real
 */
export function useRealtimeQuery<T>(
  queryKey: string[],
  queryFn: () => Promise<AxiosResponse<ApiResponse<T>>>,
  interval: number = 5000,
  config: QueryConfig<T> = {}
) {
  return useApiQuery(queryKey, queryFn, {
    refetchInterval: interval,
    refetchIntervalInBackground: true,
    staleTime: interval / 2,
    ...config,
  });
}

/**
 * Hook personalizado para operaciones con archivos
 */
export function useFileOperations() {
  const queryClient = useQueryClient();

  const useDownload = (config: MutationConfig<Blob, { url: string; filename?: string }> = {}) => {
    return useApiMutation(
      async ({ url, filename }: { url: string; filename?: string }) => {
        const response = await fetch(url);
        const blob = await response.blob();
        
        // Crear link de descarga
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename || 'download';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
        
        return blob;
      },
      {
        successMessage: 'File downloaded successfully',
        errorMessage: 'Failed to download file',
        ...config,
      }
    );
  };

  const useUpload = (config: MutationConfig<any, FormData> = {}) => {
    return useApiMutation(
      async (formData: FormData) => {
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error('Upload failed');
        }
        
        return response.json();
      },
      {
        successMessage: 'File uploaded successfully',
        errorMessage: 'Failed to upload file',
        ...config,
      }
    );
  };

  return {
    useDownload,
    useUpload,
  };
}

/**
 * Hook personalizado para operaciones de exportación
 */
export function useExportOperations() {
  const useExport = (config: MutationConfig<Blob, { type: string; params: any; format: string }> = {}) => {
    return useApiMutation(
      async ({ type, params, format }: { type: string; params: any; format: string }) => {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`/api/export/${type}?${queryString}&format=${format}`);
        
        if (!response.ok) {
          throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        
        // Descargar archivo
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${type}_export.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
        
        return blob;
      },
      {
        successMessage: 'Export completed successfully',
        errorMessage: 'Failed to export data',
        ...config,
      }
    );
  };

  return {
    useExport,
  };
} 