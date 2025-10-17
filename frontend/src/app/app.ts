import { Component, signal } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { Toast } from 'primeng/toast';
import { Loading } from './core/loading/loading';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Loading, RouterLink, Toast],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend');
}
