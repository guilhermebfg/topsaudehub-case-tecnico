import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoadingService {
  private loadingSubject = new BehaviorSubject<boolean>(false);
  public loading$: Observable<boolean> = this.loadingSubject.asObservable();

  public spinnerOn(): void {
    this.loadingSubject.next(true);
  }

  public spinnerOff(): void {
    this.loadingSubject.next(false);
  }

  public isLoading(): boolean {
    return this.loadingSubject.value;
  }
}
