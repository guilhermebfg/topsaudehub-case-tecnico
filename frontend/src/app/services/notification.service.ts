import {Injectable} from '@angular/core';
import {MessageService} from 'primeng/api';

@Injectable({
    providedIn: 'root'
})
export class NotificationService {
    constructor(private messageService: MessageService) {
    }

    public success(message: string, title: string = 'Sucesso'): void {
        this.messageService.add({
            severity: 'success', summary: title, detail: message, life: 3000
        });
    }

    public error(message: string, title: string = 'Erro'): void {
        this.messageService.add({
            severity: 'error', summary: title, detail: message, life: 5000
        });
    }

    public warning(message: string, title: string = 'Atenção'): void {
        this.messageService.add({
            severity: 'warn', summary: title, detail: message, life: 4000
        });
    }

    public info(message: string, title: string = 'Informação'): void {
        this.messageService.add({
            severity: 'info', summary: title, detail: message, life: 3000
        });
    }

    public clear(): void {
        this.messageService.clear();
    }
}
