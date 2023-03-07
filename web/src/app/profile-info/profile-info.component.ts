import { Component, Input, OnInit } from '@angular/core';

import { Profile } from '../services/profile.service';

interface PostCountYear {
  year: string
  Q1: number
  Q2: number
  Q3: number
  Q4: number
}

@Component({
  selector: 'profile-info',
  templateUrl: './profile-info.component.html',
  styleUrls: ['./profile-info.component.scss']
})
export class ProfileInfoComponent implements OnInit {
  @Input() profile?: Profile
  allColumns = ['Year', 'Q4', 'Q3', 'Q2', 'Q1']
  postCounts = []

  constructor() { }

  ngOnInit() {
  }
}
