import { Component, Input } from '@angular/core';
import { NbWindowService, NbWindowControlButtonsConfig } from '@nebular/theme';

import { ProfileService, Profile } from '../services/profile.service';
import { ProfileEditComponent } from '../profile-edit/profile-edit.component';

@Component({
  selector: 'profile-detail',
  templateUrl: './profile-detail.component.html',
  styleUrls: ['./profile-detail.component.scss']
})
export class ProfileDetailComponent {
  @Input() profile: Profile | null = null
  profileService: ProfileService

  constructor(
    profileService: ProfileService,
    private windowService: NbWindowService,
  ) {
    this.profileService = profileService
  }

  openEditWindow(username: string, display_name: string) {
    const config: NbWindowControlButtonsConfig = {
      minimize: false,
      maximize: false,
      fullScreen: false,
      close: true,
    }
    const context = { username: username, display_name: display_name }
    this.windowService.open(
      ProfileEditComponent, 
      { title: `Edit Profile: ${username}`, buttons: config, context: context }
    )
  }

  openInstagramProfile(username: string) {
    window.open(`https://www.instagram.com/${username}/`, '_blank')
  }
}
