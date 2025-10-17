import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../../environments/environment';
import {Order, OrderFormData, OrderFilterParams, OrderListResponse} from './order.model';
import {ApiResponse} from '../../models/api-response.model';

@Injectable({
    providedIn: 'root'
})
export class OrderService {
    private readonly apiUrl = `${environment.apiUrl}/orders`;

    constructor(private http: HttpClient) {
    }

    public chargeOrder(id: number): Observable<ApiResponse<Order>> {
        return this.http.put<ApiResponse<Order>>(`${this.apiUrl}/${id}/charge`, {});
    }

    public cancelOrder(id: number): Observable<ApiResponse<Order>> {
        return this.http.put<ApiResponse<Order>>(`${this.apiUrl}/${id}/cancel`, {});
    }

    public getOrders(filters?: OrderFilterParams): Observable<ApiResponse<OrderListResponse>> {
        let params = new HttpParams();

        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    params = params.set(key, value.toString());
                }
            });
        }

        return this.http.get<ApiResponse<OrderListResponse>>(this.apiUrl, {params});
    }

    public getOrder(id: number): Observable<ApiResponse<Order>> {
        return this.http.get<ApiResponse<Order>>(`${this.apiUrl}/${id}`);
    }

    public createOrder(order: OrderFormData): Observable<ApiResponse<Order>> {
        return this.http.post<ApiResponse<Order>>(this.apiUrl, order);
    }

    public updateOrder(order: OrderFormData): Observable<ApiResponse<Order>> {
        return this.http.put<ApiResponse<Order>>(this.apiUrl, order);
    }

    public deleteOrder(id: number): Observable<ApiResponse<void>> {
        return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
    }
}
