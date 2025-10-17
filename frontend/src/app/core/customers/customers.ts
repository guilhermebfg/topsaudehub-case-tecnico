import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {DatePipe} from '@angular/common';
import {firstValueFrom, Subject, takeUntil} from 'rxjs';
import {debounceTime} from 'rxjs/operators';
import {TableLazyLoadEvent, TableModule} from 'primeng/table';
import {Dialog} from 'primeng/dialog';

import {CustomerService} from './customer.service';
import {LoadingService} from '../loading/loading.service';
import {NotificationService} from '../../services/notification.service';
import {Customer, CustomerFilterParams, CustomerListResponse} from './customer.model';
import {ProductListResponse} from '../products/product.model';
import {DatePicker} from "primeng/datepicker";
import {NgxMaskDirective} from "ngx-mask";

@Component({
    selector: 'app-customers',
  imports: [TableModule, DatePipe, Dialog, ReactiveFormsModule, DatePicker, NgxMaskDirective],
    templateUrl: './customers.html',
    styleUrl: './customers.scss'
})
export class Customers implements OnInit, OnDestroy {
    public customers: CustomerListResponse = {items: [], total: 0};
    public customerForm: FormGroup;
    public customerFilter: FormGroup;
    public modalCustomerFormVisible: boolean = false;
    public today: Date = new Date();

    public loadCustomersPayload: CustomerFilterParams = {
        first: 0, rows: 5
    };

    private destroy$ = new Subject<void>();

    constructor(private customerService: CustomerService, private fb: FormBuilder, private loading: LoadingService, private notification: NotificationService) {
        this.customerForm = this.createCustomerForm();
        this.customerFilter = this.createFilterForm();
    }

    ngOnInit(): void {
        this.setupFilterSubscription();
        this.loadCustomers();
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    private createCustomerForm(): FormGroup {
        return this.fb.group({
            id: [null],
            name: [null, Validators.compose([Validators.required, Validators.minLength(3), Validators.pattern(/^\p{L}+(?: \p{L}+)*$/u)])],
            email: [null, Validators.compose([Validators.required, Validators.email])],
            document: [null, Validators.compose([Validators.required, Validators.minLength(11), Validators.maxLength(14)])],
        });
    }

    private createFilterForm(): FormGroup {
        return this.fb.group({
            id: [null], name: [null], email: [null], document: [null], created_min: [null]
        });
    }

    private setupFilterSubscription(): void {
        this.customerFilter.valueChanges
            .pipe(debounceTime(300), takeUntil(this.destroy$))
            .subscribe(() => {
                this.loadCustomers();
            });
    }

    public loadCustomers(event: TableLazyLoadEvent | null = null): void {
        if (event?.rows != null) {
            this.loadCustomersPayload.rows = event.rows;
        }
        if (event?.first != null) {
            this.loadCustomersPayload.first = event.first;
        }

        const filter = this.customerFilter.getRawValue();

        const payload: CustomerFilterParams = {
            name: filter.name ?? '',
            email: filter.email ? encodeURIComponent(filter.email) : '',
            document: filter.document ?? '',
            created_min: filter.created_min ? new Date(filter.created_min).toISOString() : '',
            first: this.loadCustomersPayload.first,
            rows: this.loadCustomersPayload.rows
        };

        this.customerService.getCustomers(payload)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
                next: (res) => {
                    this.customers = res.data;
                }, error: (error) => {
                    console.error('Error loading customers:', error);
                }
            });
    }

    public get customerId(): number | null {
        return this.customerForm.get('id')?.value;
    }

    public openModalFormCustomer(customerId: number | null = null): void {
        if (customerId != null) {
            const customer = this.customers.items.find((c: Customer) => c.id === customerId);
            if (customer) {
                this.customerForm.patchValue(customer);
            }
        } else {
            this.customerForm.reset();
        }

        this.modalCustomerFormVisible = true;
    }

    public async saveCustomer(): Promise<void> {
        if (!this.customerForm.valid) {
            this.notification.warning('Por favor, preencha todos os campos obrigatórios');
            this.customerForm.markAllAsTouched();
            return;
        }

        this.loading.spinnerOn();

        const payload = this.customerForm.getRawValue();

        try {
            if (payload.id != null) {
                await firstValueFrom(this.customerService.updateCustomer(payload));
                this.notification.success('Cliente atualizado com sucesso');
            } else {
                await firstValueFrom(this.customerService.createCustomer(payload));
                this.notification.success('Cliente cadastrado com sucesso');
            }

            this.loadCustomers();
            this.modalCustomerFormVisible = false;
        } catch (error) {
            console.error('Error saving customer:', error);
        } finally {
            this.loading.spinnerOff();
        }
    }
}
