import {HttpInterceptorFn, HttpErrorResponse} from '@angular/common/http';
import {inject} from '@angular/core';
import {catchError, throwError} from 'rxjs';
import {NotificationService} from '../services/notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
    const notificationService = inject(NotificationService);

    return next(req).pipe(catchError((error: HttpErrorResponse) => {
        let errorMessage = 'Ocorreu um erro inesperado';

        if (error.error instanceof ErrorEvent) {
            errorMessage = `Erro: ${error.error.message}`;
        } else {
            switch (error.status) {
                case 400:
                    errorMessage = error.error?.message || 'Dados inválidos';
                    break;
                case 401:
                    errorMessage = 'Não autorizado';
                    break;
                case 403:
                    errorMessage = 'Acesso negado';
                    break;
                case 404:
                    errorMessage = 'Recurso não encontrado';
                    break;
                case 422:
                    errorMessage = error.error?.message || 'Erro de validação';
                    break;
                case 409:
                    errorMessage = 'Item já foi cadastrado anteriormente';
                    break
                case 500:
                    errorMessage = 'Erro interno do servidor';
                    break;
                case 0:
                    errorMessage = 'Não foi possível se conectar';
                    break;
                default:
                    errorMessage = error.error?.message || `Erro ${error.status}: ${error.statusText}`;
            }
        }

        notificationService.error(errorMessage);

        return throwError(() => error);
    }));
};
