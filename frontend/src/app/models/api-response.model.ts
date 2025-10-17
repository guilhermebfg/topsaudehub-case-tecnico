export interface ApiResponse<T> {
    data: T;
    message?: string;
}

export interface PaginatedResponse<T> {
    data: {
        items: T[]; total: number;
    };
    message?: string;
}
