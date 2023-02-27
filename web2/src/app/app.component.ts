import { Component } from '@angular/core';

import { NbSidebarService, NbThemeService } from '@nebular/theme';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'InstaArchiver';

  constructor(private sidebarService: NbSidebarService, private themeService: NbThemeService) {
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
      e.matches && this.themeService.changeTheme('default')
    })
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      e.matches && this.themeService.changeTheme('dark')
    })
  }

  toggle() {
    this.sidebarService.toggle(true, 'left')
  }
}
