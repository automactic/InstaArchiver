import { Component, OnInit } from '@angular/core';

import { ProfileService } from '../services/profile.service';


@Component({
  selector: 'app-profiles',
  templateUrl: './profiles.component.html',
  styleUrls: ['./profiles.component.scss']
})
export class ProfilesComponent implements OnInit {
  profileService: ProfileService;
  
  constructor(profileService: ProfileService) {
    this.profileService = profileService;
  }

  ngOnInit(): void { }
}
