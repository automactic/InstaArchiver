import { Component } from '@angular/core';

import { ProfileService } from './services/profile.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'InstaArchiver';
  profileService: ProfileService;

  constructor(
    profileService: ProfileService
  ) {
    this.profileService = profileService;
  }
}
