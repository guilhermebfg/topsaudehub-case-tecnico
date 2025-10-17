import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../../environments/environment';
import {Product, ProductFormData, ProductFilterParams, ProductListResponse} from './product.model';
import {ApiResponse, PaginatedResponse} from '../../models/api-response.model';

@Injectable({
    providedIn: 'root'
})
export class ProductService {
    private readonly apiUrl = `${environment.apiUrl}/products`;

    constructor(private http: HttpClient) {
    }

    public getProducts(filters?: ProductFilterParams): Observable<ApiResponse<ProductListResponse>> {
        let params = new HttpParams();

        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    params = params.set(key, value.toString());
                }
            });
        }

        return this.http.get<ApiResponse<ProductListResponse>>(this.apiUrl, {params});
    }

    public getProduct(id: number): Observable<ApiResponse<Product>> {
        return this.http.get<ApiResponse<Product>>(`${this.apiUrl}/${id}`);
    }

    public createProduct(product: ProductFormData): Observable<ApiResponse<Product>> {
        return this.http.post<ApiResponse<Product>>(this.apiUrl, product);
    }

    public updateProduct(product: ProductFormData): Observable<ApiResponse<Product>> {
        return this.http.put<ApiResponse<Product>>(this.apiUrl, product);
    }

    public deleteProduct(id: number): Observable<ApiResponse<void>> {
        return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
    }

    public searchProducts(query: string): Observable<ApiResponse<ProductListResponse>> {
        const params = new HttpParams()
            .set('name', query)
            .set('is_active', true)
            .set('stock_qty', 1);
        return this.http.get<ApiResponse<ProductListResponse>>(this.apiUrl, {params});
    }
}
