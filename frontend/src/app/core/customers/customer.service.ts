import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../../environments/environment';
import {Customer, CustomerFormData, CustomerFilterParams, CustomerListResponse} from './customer.model';
import {ApiResponse} from '../../models/api-response.model';

@Injectable({
    providedIn: 'root'
})
export class CustomerService {
    private readonly apiUrl = `${environment.apiUrl}/customers`;

    constructor(private http: HttpClient) {
    }

    public getCustomers(filters?: CustomerFilterParams): Observable<ApiResponse<CustomerListResponse>> {
        let params = new HttpParams();

        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    params = params.set(key, value.toString());
                }
            });
        }

        return this.http.get<ApiResponse<CustomerListResponse>>(this.apiUrl, {params});
    }

    public getCustomer(id: number): Observable<ApiResponse<Customer>> {
        return this.http.get<ApiResponse<Customer>>(`${this.apiUrl}/${id}`);
    }

    public createCustomer(customer: CustomerFormData): Observable<ApiResponse<Customer>> {
        return this.http.post<ApiResponse<Customer>>(this.apiUrl, customer);
    }

    public updateCustomer(customer: CustomerFormData): Observable<ApiResponse<Customer>> {
        return this.http.put<ApiResponse<Customer>>(this.apiUrl, customer);
    }

    public deleteCustomer(id: number): Observable<ApiResponse<void>> {
        return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
    }
}
