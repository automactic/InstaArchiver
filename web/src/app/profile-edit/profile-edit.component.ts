import { Component } from '@angular/core';
import { NbWindowRef } from '@nebular/theme';

import { ProfileService } from '../services/profile.service';

@Component({
  selector: 'app-profile-edit',
  templateUrl: './profile-edit.component.html',
  styleUrls: ['./profile-edit.component.scss']
})
export class ProfileEditComponent {
  username: string
  display_name: string

  constructor(protected windowRef: NbWindowRef, private profileService: ProfileService) {
    const context = windowRef.config.context as { username: string, display_name: string }
    this.username = context.username
    this.display_name = context.display_name
  }

  update() {
    this.profileService.update(this.username, this.display_name)
    this.windowRef.close()
  }
}
