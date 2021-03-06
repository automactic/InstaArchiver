import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { ProfileService, Profile, ProfileConfiguration } from '../services/profile.service';


@Component({
  selector: 'app-profile-detail',
  templateUrl: './profile-detail.component.html',
  styleUrls: ['./profile-detail.component.scss']
})
export class ProfileDetailComponent implements OnInit {
  profileService: ProfileService;
  
  profile$: Observable<Profile>;
  configuration = new ProfileConfiguration()

  constructor(private route: ActivatedRoute, profileService: ProfileService) {
    this.profileService = profileService;
    this.profile$ = this.route.paramMap.pipe(
      switchMap(params => {
        return this.profileService.get(params.get("username") ?? "")
      })
    );
    this.profile$.subscribe( profile => {
      this.configuration.display_name = profile.display_name
      this.configuration.auto_archive = profile.auto_archive
    })
  }

  ngOnInit(): void { }

  openInstagramProfile(username: string) {
    window.open(`https://www.instagram.com/${username}/`, '_blank');
  }

}
