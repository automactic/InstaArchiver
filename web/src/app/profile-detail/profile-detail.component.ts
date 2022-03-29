import { Component, Input } from '@angular/core';

import { Profile } from '../services/profile.service';

@Component({
  selector: 'profile-detail',
  templateUrl: './profile-detail.component.html',
  styleUrls: ['./profile-detail.component.scss']
})
export class ProfileDetailComponent {
  @Input() profile?: Profile

  constructor() { }
}
