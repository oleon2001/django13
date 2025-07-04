import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { AxiosError, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';
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
  const message = customMessage || (error.response?.data as any)?.message || error.message || 'An error occurred';
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
    queryFn: async (): Promise<T> => {
      try {
        const response = await queryFn();
        return (response.data.data || response.data) as T;
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
  config: QueryConfig<{ data: T[]; pagination: any }> = {}
) {
  const {
    showErrorToast = true,
    errorMessage,
    ...queryConfig
  } = config;

  return useQuery({
    queryKey: [...queryKey, params],
    queryFn: async (): Promise<{ data: T[]; pagination: any }> => {
      try {
        const response = await queryFn(params);
        return {
          data: (response.data.data || response.data) as T[],
          pagination: (response.data as any).pagination,
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
    mutationFn: async (variables: TVariables): Promise<TData> => {
      try {
        const response = await mutationFn(variables);
        const data = (response.data.data || response.data) as TData;
        
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
    mutationFn: async (variables: TVariables): Promise<TData> => {
      try {
        const response = await mutationFn(variables);
        const data = (response.data.data || response.data) as TData;
        
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
    onMutate: async (newItem: TVariables): Promise<{ previousData: TData[] | undefined } | undefined> => {
      // Cancelar queries en curso
      await queryClient.cancelQueries({ queryKey });
      
      // Guardar datos anteriores
      const previousData = queryClient.getQueryData<TData[]>(queryKey);
      
      // Optimistic update
      queryClient.setQueryData<TData[]>(queryKey, (old) => {
        return old ? updateFn(old, newItem as unknown as TData) : [newItem as unknown as TData];
      });
      
      return { previousData };
    },
    onError: (_err, _newItem, context) => {
      // Revertir en caso de error
      const typedContext = context as { previousData: TData[] | undefined } | undefined;
      if (typedContext?.previousData) {
        queryClient.setQueryData(queryKey, typedContext.previousData);
      }
    },
    onSettled: () => {
      // Invalidar y refetch
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
  const useGetAll = (params: PaginationParams = {}, config: QueryConfig<{ data: T[]; pagination: any }> = {}) => {
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
  const useDownload = (config: MutationConfig<Blob, { url: string; filename?: string }> = {}) => {
    return useMutation({
      mutationFn: async ({ url, filename }: { url: string; filename?: string }): Promise<Blob> => {
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
      ...config,
    });
  };

  const useUpload = (config: MutationConfig<any, FormData> = {}) => {
    return useMutation({
      mutationFn: async (formData: FormData): Promise<any> => {
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error('Upload failed');
        }
        
        return response.json();
      },
      ...config,
    });
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
    return useMutation({
      mutationFn: async ({ type, params, format }: { type: string; params: any; format: string }): Promise<Blob> => {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`/api/export/${type}?${queryString}&format=${format}`);
        
        if (!response.ok) {
          throw new Error('Export failed');
        }
        
        return response.blob();
      },
      ...config,
    });
  };

  return {
    useExport,
  };
} 