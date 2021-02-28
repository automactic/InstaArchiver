import { Component, OnInit } from '@angular/core';

import { ProfileService } from '../services/profile.service';


@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent implements OnInit {
  profileService: ProfileService;
  
  constructor(profileService: ProfileService) {
    this.profileService = profileService;
  }

  ngOnInit(): void {
  }

}
